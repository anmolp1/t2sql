from typing import Dict, Any, Optional, List
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.core.config import settings
from app.models.database_connection import DatabaseConnection
from app.models.database_metadata import DatabaseMetadata

class SQLQuery(BaseModel):
    sql_query: str = Field(description="The generated SQL query")
    explanation: str = Field(description="Explanation of what the query does")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the query")

class SQLGenerationService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4",
            temperature=0
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SQLQuery)

    def _create_prompt(
        self,
        question: str,
        metadata: DatabaseMetadata,
        connection: DatabaseConnection,
        use_cases: Optional[List[Dict[str, str]]] = None
    ) -> str:
        # Create a comprehensive prompt that includes:
        # 1. Database schema and relationships
        # 2. Use cases and examples if available
        # 3. The user's question
        # 4. Instructions for the model
        
        # Format datasets and tables information
        datasets_info = "\n".join([
            f"Dataset: {dataset['name']}\n" +
            "Tables:\n" + "\n".join([
                f"  - {table['name']}\n" +
                f"    Columns: {', '.join([f'{col['name']} ({col['type']})' for col in table['columns']])}"
                for table in dataset['tables']
            ])
            for dataset in metadata.datasets
        ])
        
        use_cases_info = ""
        if use_cases:
            use_cases_info = "\nUse Cases:\n" + "\n".join([
                f"- Question: {case['natural_language_example']}\n" +
                f"  Query: {case['example_query']}"
                for case in use_cases
            ])

        prompt_template = f"""You are a BigQuery SQL expert that converts natural language questions into SQL queries.

Schema Information:
{datasets_info}

{use_cases_info}

Question: {question}

Generate a BigQuery SQL query that answers this question. Follow these rules:
1. Use appropriate JOIN clauses based on the table relationships
2. Include clear column names (dataset.table.column) to avoid ambiguity
3. Use appropriate WHERE clauses to filter data
4. Use appropriate GROUP BY and aggregation functions when needed
5. Use BigQuery-specific functions and syntax
6. Ensure the query is optimized for BigQuery performance
7. Use appropriate date/time functions for BigQuery
8. Consider BigQuery's columnar storage model when writing queries

{self.output_parser.get_format_instructions()}"""

        return prompt_template

    async def generate_sql(
        self,
        question: str,
        metadata: DatabaseMetadata,
        connection: DatabaseConnection,
        use_cases: Optional[List[Dict[str, str]]] = None
    ) -> SQLQuery:
        """Generate SQL query from natural language question."""
        prompt = ChatPromptTemplate.from_template(self._create_prompt(
            question, metadata, connection, use_cases
        ))
        
        chain = prompt | self.llm | self.output_parser
        result = await chain.ainvoke({"input": question})
        
        return result 