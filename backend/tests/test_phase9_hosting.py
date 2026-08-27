from pathlib import Path

TEMPLATE = (Path(__file__).parents[2] / "template.yaml").read_text(encoding="utf-8")


def test_frontend_origin_is_private_and_uses_oac() -> None:
    assert "AWS::CloudFront::OriginAccessControl" in TEMPLATE
    assert "SigningBehavior: always" in TEMPLATE
    assert "OriginAccessControlOriginType: s3" in TEMPLATE
    assert "BlockPublicAcls: true" in TEMPLATE
    assert "RestrictPublicBuckets: true" in TEMPLATE
    assert "WebsiteConfiguration" not in TEMPLATE
    assert "Principal: '*'" not in TEMPLATE


def test_cloudfront_is_https_only_and_source_arn_scoped() -> None:
    assert "ViewerProtocolPolicy: redirect-to-https" in TEMPLATE
    assert "MinimumProtocolVersion: TLSv1.2_2021" in TEMPLATE
    assert "AWS:SourceArn:" in TEMPLATE
    assert "Service: cloudfront.amazonaws.com" in TEMPLATE
    assert "PriceClass: PriceClass_100" in TEMPLATE


def test_production_origin_is_added_to_auth_and_cors() -> None:
    cloudfront_origin = "!Sub https://${FrontendDistribution.DomainName}"
    assert TEMPLATE.count(cloudfront_origin) >= 3
    assert "FrontendUrl:" in TEMPLATE
    assert "FrontendBucketName:" in TEMPLATE
    assert "FrontendDistributionId:" in TEMPLATE
