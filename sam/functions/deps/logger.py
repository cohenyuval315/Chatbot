from aws_lambda_powertools import Logger
import logging

logger = Logger(serialize_stacktrace=True,level=logging.DEBUG)