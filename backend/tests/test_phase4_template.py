from pathlib import Path

TEMPLATE = (Path(__file__).parents[2] / "template.yaml").read_text(encoding="utf-8")


def test_phase4_uses_only_approved_vector_architecture() -> None:
    assert "AWS::S3Vectors::VectorBucket" in TEMPLATE
    assert "AWS::S3Vectors::Index" in TEMPLATE
    assert "AWS::Bedrock::KnowledgeBase" in TEMPLATE
    assert "amazon.titan-embed-text-v2:0" in TEMPLATE
    assert "AWS::OpenSearchServerless" not in TEMPLATE
    assert "s3vectors:QueryVectors" in TEMPLATE
    assert "s3vectors:PutVectors" in TEMPLATE


def test_chunking_is_bounded_without_advanced_parser() -> None:
    assert "ChunkingStrategy: FIXED_SIZE" in TEMPLATE
    assert "MaxTokens: 300" in TEMPLATE
    assert "OverlapPercentage: 20" in TEMPLATE
    assert "SEMANTIC" not in TEMPLATE
    assert "HIERARCHICAL" not in TEMPLATE
    assert "ParsingConfiguration" not in TEMPLATE


def test_gate_c_generation_is_not_present() -> None:
    assert "RetrieveAndGenerate" not in TEMPLATE
    assert "bedrock:InvokeModelWithResponseStream" not in TEMPLATE
