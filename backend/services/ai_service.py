import os
import time
from dataclasses import dataclass
from typing import List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


class GeneratedSection(BaseModel):
    section_name: str = Field(
        description="The exact name of the section, copied verbatim from the request"
    )
    content: str = Field(description="The generated content for this section")


class GeneratedDoc(BaseModel):
    sections: List[GeneratedSection] = Field(
        description="All requested document sections, in order"
    )


@dataclass
class LLMUsage:
    """Token usage + metadata captured from a single LLM call."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int


class AIDocumentService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
        )
        # include_raw=True so we keep the raw AIMessage (with usage_metadata)
        # alongside the parsed structured output.
        self.structured_llm = llm.with_structured_output(GeneratedDoc, include_raw=True)

    def _extract_usage(self, raw, latency_ms: int) -> LLMUsage:
        usage_meta = getattr(raw, "usage_metadata", None) or {}
        prompt = int(usage_meta.get("input_tokens") or 0)
        completion = int(usage_meta.get("output_tokens") or 0)
        total = int(usage_meta.get("total_tokens") or (prompt + completion))
        response_meta = getattr(raw, "response_metadata", None) or {}
        model = response_meta.get("model_name") or self.model_name
        return LLMUsage(
            model=model,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
            latency_ms=latency_ms,
        )

    async def _invoke(self, messages):
        """Invoke the LLM, returning (parsed GeneratedDoc | None, LLMUsage)."""
        start = time.perf_counter()
        result = await self.structured_llm.ainvoke(messages)
        latency_ms = int((time.perf_counter() - start) * 1000)
        parsed = result.get("parsed") if isinstance(result, dict) else result
        raw = result.get("raw") if isinstance(result, dict) else None
        return parsed, self._extract_usage(raw, latency_ms)

    @staticmethod
    def _section_name(section, index: int) -> str:
        return (
            section.section_template.name
            if section.section_template
            else f"Section {index + 1}"
        )

    def _build_system_prompt(
        self, sections: list, document_type_system_prompt: Optional[str]
    ) -> str:
        base = document_type_system_prompt or (
            "You are a professional document writer. Write clear, concise, and well-structured content."
        )
        parts = [
            base,
            "",
            "Generate content for each of the following sections. "
            "Return every section using its exact name as given below.",
        ]
        for i, s in enumerate(sections):
            parts.append(f"\nSection: {self._section_name(s, i)}")
            if s.section_template and s.section_template.system_prompt:
                parts.append(f"Instructions: {s.section_template.system_prompt}")
            if s.section_template and s.section_template.content_structure:
                parts.append(
                    f"Expected structure: {s.section_template.content_structure}"
                )
        return "\n".join(parts)

    def _map_back(self, sections: list, generated) -> dict:
        gen_sections = (
            generated.sections
            if hasattr(generated, "sections")
            else (generated or {}).get("sections", [])
        )

        def name_of(gs):
            return (
                (
                    gs.section_name
                    if hasattr(gs, "section_name")
                    else gs.get("section_name", "")
                )
                .strip()
                .lower()
            )

        def content_of(gs):
            return gs.content if hasattr(gs, "content") else gs.get("content", "")

        by_name = {name_of(gs): content_of(gs) for gs in gen_sections}

        full_alignment = len(gen_sections) == len(sections)

        result = {}
        for i, s in enumerate(sections):
            name = self._section_name(s, i).strip().lower()
            if name in by_name:
                result[s.document_section_id] = by_name[name]
            elif full_alignment:
                result[s.document_section_id] = content_of(gen_sections[i])
        return result

    async def generate_document(
        self,
        sections: list,
        user_prompt: str,
        document_type_system_prompt: Optional[str],
    ) -> tuple[dict, LLMUsage]:
        messages = [
            SystemMessage(
                content=self._build_system_prompt(sections, document_type_system_prompt)
            ),
            HumanMessage(content=user_prompt or "Generate the document."),
        ]
        generated, usage = await self._invoke(messages)
        return self._map_back(sections, generated), usage

    async def refine_document(
        self,
        sections: list,
        conversation: list,
        document_type_system_prompt: Optional[str],
    ) -> tuple[dict, LLMUsage]:
        """conversation: ordered list of {role: 'user'|'assistant', text: str} held by the frontend
        for the current generation session (initial prompt, each generated draft, each refinement)."""
        messages = [
            SystemMessage(
                content=self._build_system_prompt(sections, document_type_system_prompt)
            )
        ]
        for turn in conversation or []:
            role = turn.get("role")
            text = turn.get("text") or turn.get("content") or ""
            if role == "user":
                messages.append(HumanMessage(content=text))
            elif role == "assistant":
                messages.append(AIMessage(content=text))
        if len(messages) == 1:
            messages.append(HumanMessage(content="Generate the document."))
        generated, usage = await self._invoke(messages)
        return self._map_back(sections, generated), usage
