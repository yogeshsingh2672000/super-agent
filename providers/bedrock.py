"""AWS Bedrock (Claude, gpt-oss and other Bedrock models)."""
import boto3

import config
from utils.env import env, env_bool, env_float

NAME = "AWS Bedrock"
SETTINGS = {
    "region": env("BEDROCK_REGION", "ap-south-1"),
    "model": env("BEDROCK_MODEL"),
    "input_price": env_float("BEDROCK_INPUT_PRICE_PER_M"),
    "output_price": env_float("BEDROCK_OUTPUT_PRICE_PER_M"),
    "vision": env_bool("BEDROCK_VISION", True),
}


def status() -> tuple[bool, str]:
    if not SETTINGS["model"]:
        return False, "BEDROCK_MODEL missing in .env"
    if boto3.Session().get_credentials() is None:
        return False, "no AWS credentials (set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY or run aws configure)"
    return True, f"region {SETTINGS['region']}"


def build(callbacks: list):
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=SETTINGS["model"],
        region_name=SETTINGS["region"],
        max_tokens=config.MAX_TOKENS,
        callbacks=callbacks,
    )
