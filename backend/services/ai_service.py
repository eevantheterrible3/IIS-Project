import asyncio
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AIDocumentService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            google_api_key=api_key,
        )

    async def _generate_section(
        self,
        document_type_system_prompt: str | None,
        section_name: str,
        section_system_prompt: str | None,
        section_content_structure: str | None,
        user_prompt: str,
    ) -> str:
        system = document_type_system_prompt or (
            "You are a professional document writer. Write clear, concise, and well-structured content."
        )

        human_parts = [
            f"Generate content for the following document section.\n\nSection: {section_name}",
        ]
        if section_system_prompt:
            human_parts.append(f"Section instructions: {section_system_prompt}")
        if section_content_structure:
            human_parts.append(f"Expected structure: {section_content_structure}")
        human_parts.append(f"\nUser's request: {user_prompt}")
        human_parts.append("\nWrite the section content:")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system}"),
            ("human", "{human}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"system": system, "human": "\n\n".join(human_parts)})

    async def generate_all_sections(
        self,
        sections: list,
        user_prompt: str,
        document_type_system_prompt: str | None,
    ) -> dict:
        tasks = [
            self._generate_section(
                document_type_system_prompt=document_type_system_prompt,
                section_name=s.section_template.name if s.section_template else f"Section {i + 1}",
                section_system_prompt=s.section_template.system_prompt if s.section_template else None,
                section_content_structure=s.section_template.content_structure if s.section_template else None,
                user_prompt=user_prompt,
            )
            for i, s in enumerate(sections)
        ]
        results = await asyncio.gather(*tasks)
        return {s.document_section_id: content for s, content in zip(sections, results)}
