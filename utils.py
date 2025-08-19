from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from prompts import JURISDICTION_SUBSTANCE_EXTRACTION
from schema import Jurisdiction, Jurisdictions

load_dotenv()

MODEL = "gemma-3-4b-it"
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0.25)


def extract_jurisdiction(text: str) -> list[Jurisdiction]:
    parser = PydanticOutputParser(pydantic_object=Jurisdictions)
    template = PromptTemplate.from_template(JURISDICTION_SUBSTANCE_EXTRACTION)
    chain = template | llm | parser

    result: Jurisdictions = chain.invoke(
        {"text": text, "format_instructions": parser.get_format_instructions()}
    )

    if result.jurisdictions == None:
        return []

    return [juridiction for juridiction in result.jurisdictions]
