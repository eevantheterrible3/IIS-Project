import json
import os
import re
import httpx


class AiTagService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    async def suggest_tags(self, document_name: str, document_text: str) -> list[str]:
        prompt = self._build_prompt(document_name, document_text)

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 200,
                    },
                },
            )

        response.raise_for_status()

        data = response.json()
        raw_response = data.get("response", "")

        return self._parse_tags(raw_response)

    def _build_prompt(self, document_name: str, document_text: str) -> str:
        return f"""
You are a document tagging assistant.

Your task is to generate tags for a document.

Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.
Do not include text before or after JSON.

Required JSON format:
{{
  "tags": ["tag1", "tag2", "tag3"]
}}

Rules:
- Generate 3 to 7 tags.
- Tags must be short.
- Tags must be useful for search.
- Tags must be written in English.
- Tags must not be full sentences.

Document name:
{document_name}

Document content:
{document_text[:5000]}
"""

    def _parse_tags(self, raw_response: str) -> list[str]:
        raw_response = raw_response.strip()

        if not raw_response:
            return []

        tags = self._try_parse_json_tags(raw_response)

        if not tags:
            tags = self._try_extract_json_object(raw_response)

        if not tags:
            tags = self._try_extract_list_items(raw_response)

        return self._clean_tags(tags)

    def _try_parse_json_tags(self, raw_response: str) -> list[str]:
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            return []

        return self._get_tags_from_parsed_json(parsed)

    def _try_extract_json_object(self, raw_response: str) -> list[str]:
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)

        if not match:
            return []

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []

        return self._get_tags_from_parsed_json(parsed)

    def _get_tags_from_parsed_json(self, parsed) -> list[str]:
        if isinstance(parsed, dict):
            tags = parsed.get("tags", [])

            if isinstance(tags, list):
                return tags

            if isinstance(tags, str):
                return [tag.strip() for tag in tags.split(",")]

        if isinstance(parsed, list):
            return parsed

        return []

    def _try_extract_list_items(self, raw_response: str) -> list[str]:
        lines = raw_response.splitlines()
        tags = []

        for line in lines:
            cleaned_line = line.strip()
            cleaned_line = cleaned_line.lstrip("-*•0123456789. ")
            cleaned_line = cleaned_line.strip('"').strip("'").strip(",")

            if cleaned_line:
                tags.append(cleaned_line)

        return tags

    def _clean_tags(self, tags: list) -> list[str]:
        cleaned_tags = []

        for tag in tags:
            if not isinstance(tag, str):
                continue

            cleaned_tag = tag.strip().lower()
            cleaned_tag = re.sub(r"[^a-z0-9\s\-]", "", cleaned_tag)
            cleaned_tag = re.sub(r"\s+", " ", cleaned_tag).strip()

            if not cleaned_tag:
                continue

            if len(cleaned_tag) > 40:
                continue

            already_exists = any(
                existing.lower() == cleaned_tag.lower()
                for existing in cleaned_tags
            )

            if not already_exists:
                cleaned_tags.append(cleaned_tag)

        return cleaned_tags[:7]