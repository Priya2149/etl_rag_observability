from shared.llm import (
    GroundedAnswer,
    LLMProvider,
    LLMRequest,
    StructuredLLMResult,
    get_configured_provider,
)

GROUNDING_INSTRUCTIONS = """You answer questions using only the retrieved context.
If the context is insufficient, say so rather than using outside knowledge.
Only cite source identifiers that are explicitly provided with the context."""


def build_rag_request(query: str, retrieval: dict) -> LLMRequest:
    context = []
    for index, chunk in enumerate(retrieval["retrieved_chunks"], start=1):
        source = chunk.get("metadata", {}).get("source", "unknown")
        context.append(f"[{index}] Source: {source}\n{chunk['content']}")

    prompt = f"Question:\n{query}\n\nRetrieved context:\n"
    prompt += "\n\n".join(context) if context else "No context was retrieved."

    return LLMRequest(
        input=prompt,
        instructions=GROUNDING_INSTRUCTIONS,
        context=[chunk["content"] for chunk in retrieval["retrieved_chunks"]],
        sources=retrieval["source_files"],
    )


def generate_rag_answer(
    query: str,
    retrieval: dict,
    provider: LLMProvider | None = None,
) -> StructuredLLMResult[GroundedAnswer]:
    provider = provider or get_configured_provider()
    request = build_rag_request(query, retrieval)
    result = provider.generate_structured(request, GroundedAnswer)

    allowed_sources = set(request.sources)
    grounded_output = GroundedAnswer(
        answer=result.output.answer,
        sources=[
            source for source in result.output.sources if source in allowed_sources
        ],
    )
    return result.model_copy(update={"output": grounded_output})
