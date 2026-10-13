test_questions = [
    {
        "question": "Why must a heat removal path remain available after a CANDU reactor is shut down?",
        "answer": "Because fission products continue to generate decay heat after shutdown. A heat removal path and heat sink must therefore remain available whenever used fuel is present to remove this decay heat."
    },

    {
        "question": "What percentage of full reactor power is typically produced by fission-product decay immediately after shutdown, and approximately how much does it decrease to after one hour?",
        "answer": "At power, fission-product decay contributes typically 6–7% of full power. About one hour after shutdown, it typically decreases to around 1% of full power."
    },

    {
        "question": "Why are the cooling systems used for decay-heat removal supplied by Class III power?",
        "answer": "Because decay heat continues to exist after shutdown, the cooling systems require a reliable power supply. They are therefore supplied by, or backed up by, Class III power."
    },

    {
        "question": "What is the difference between direct and indirect shutdown cooling?",
        "answer": "In direct shutdown cooling, the HT D2O is cooled directly by service water. In indirect shutdown cooling, heat is transferred first from HTS coolant to boiler feedwater through preheaters, and then from the feedwater to service water before reaching the final heat sink."
    },

    {
        "question": "Why does an indirect shutdown cooling system require the boiler feedwater system to remain in service?",
        "answer": "Because the indirect system transfers heat from the HTS coolant to boiler feedwater through external preheaters. The feedwater system therefore has to operate, and the HT pumps must also remain in operation."
    },

    {
        "question": "Why is a Maintenance Cooling System provided on units that use indirect shutdown cooling?",
        "answer": "The Maintenance Cooling System allows the feedwater system and HT pumps to be shut down when maintenance is required on the feedwater or HT system."
    },

    {
        "question": "What is the approximate heat-removal capacity of the Maintenance Cooling System?",
        "answer": "The Maintenance Cooling System has a heat-removal capacity of approximately 1% of full reactor power."
    },

    {
        "question": "What final HTS condition can an indirect shutdown cooling system achieve, and what system is used to reach a cold depressurized state?",
        "answer": "Indirect shutdown cooling can bring the HTS to a cold pressurized state. The Maintenance Cooling System is used to take the HTS to a cold depressurized state."
    },

    {
        "question": "What happens if the main HT pumps are lost during indirect shutdown cooling?",
        "answer": "Heat removal through the preheaters becomes inadequate. Thermosyphoning is then required to remove the heat that had been removed through the preheater until maintenance cooling is put into service."
    },

    {
        "question": "Why must the feedwater portion of the indirect shutdown cooling system remain pressurized?",
        "answer": "If it is not kept pressurized, boiling can occur. The resulting vapor pockets can collapse when condensed in the heat exchanger or when the system is rapidly pressurized, potentially causing water hammer."
    },

    {
        "question": "How is thermosyphoning achieved in a CANDU reactor?",
        "answer": "Thermosyphoning is achieved by natural convection between the reactor and boilers. Hot D2O rises to the boilers, where it is cooled by boiler water, becomes denser, and falls back toward the reactor."
    },

    {
        "question": "What four conditions are required to maintain thermosyphoning?",
        "answer": "The four conditions are: reactor power must be ≤3% full power; Boiler Pressure Control must be functional to maintain the required temperature difference; SRVs or ASDV valves must be available with a feedwater supply for heat rejection; and HTS pressure and inventory control must be available to prevent HTS boiling."
    },

    {
        "question": "Approximately how much reactor full power can thermosyphoning remove?",
        "answer": "Thermosyphoning is capable of removing approximately 3% of reactor full power."
    },

    {
        "question": "How is the initial cooldown from full power normally achieved before shutdown cooling continues the cooldown?",
        "answer": "For both direct and indirect systems, the initial HTS cooldown from approximately 300°C to about 150–165°C is normally achieved using the Boiler Pressure Control system through steam discharge to the atmosphere or condenser. Shutdown cooling then continues the cooldown."
    },

    {
        "question": "How can an emergency cooldown be performed if normal Boiler Pressure Control cooldown is unavailable?",
        "answer": "Emergency cooldown can be achieved by immediately putting the shutdown cooling system into service following a trip, using the shutdown coolers without a prior warmup."
    },

    {
        "question": "What is the normal maximum capacity requirement of the shutdown coolers during an emergency cooldown?",
        "answer": "The normal maximum capacity requirement is approximately 6–7% of full reactor thermal power."
    },

    {
        "question": "Why can emergency cooldown using shutdown coolers only be performed a limited number of times?",
        "answer": "Putting the shutdown cooling system into service at elevated temperature subjects the system to high thermal stresses and thermal shock. The equipment is designed to withstand this only a limited number of times; reaching the limit can require extensive repairs, inspections, or equipment replacement."
    },

    {
        "question": "What inspection is required after an emergency cooldown using the shutdown coolers?",
        "answer": "A thorough inspection of the shutdown coolers must be performed, and tube-sheet integrity must be assured."
    },

    {
        "question": "What is crash cooldown and how is it performed?",
        "answer": "Crash cooldown is a rapid reduction in HTS temperature caused by discharging large amounts of boiler steam to the atmosphere. The heat-transfer path involves coolant flowing to the boilers and steam being discharged to the atmosphere through the available steam discharge valves."
    },

    {
        "question": "What oxygen concentration range is required before workers can enter a confined space?",
        "answer": "The oxygen concentration must be between 19.5% and 21.4%. If necessary, the confined space must be purged or ventilated before entry."
    }
]

import os

from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.evaluate import AsyncConfig

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


# ============================================================
# CONFIG
# ============================================================

CHROMA_DIR = "./vector_db"

TOP_K = 5


# ============================================================
# EMBEDDINGS
# ============================================================

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


# ============================================================
# LOAD CHROMA COLLECTIONS
# ============================================================

fixed_db = Chroma(
    collection_name="normal_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

semantic_db = Chroma(
    collection_name="semantic_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

hybrid_db = Chroma(
    collection_name="hybrid_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)


# ============================================================
# DEEPEVAL JUDGE MODEL
# ============================================================

from deepeval.models import OllamaModel

judge_model = OllamaModel(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0,
)



def retrieve(db, question):

    docs = db.similarity_search(
        question,
        k=TOP_K
    )

    return docs


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(question, context):
    """
    For the first experiment, we don't actually need an LLM
    generation step.

    We use the retrieved context as actual_output so we can
    evaluate retrieval quality independently.

    Later, replace this with your RAG chain.
    """

    return "\n\n".join(
        doc.page_content
        for doc in context
    )


# ============================================================
# CREATE DEEPEVAL TEST CASES
# ============================================================

def create_test_cases(db, strategy):

    test_cases = []

    for i in range(10):

        question = test_questions[i]["question"]
        expected_answer = test_questions[i]["answer"]

        # Retrieve chunks
        docs = retrieve(
            db,
            question
        )

        # Convert Documents -> strings
        retrieval_context = [
            doc.page_content
            for doc in docs
        ]

        # For now, use retrieved context as actual output
        actual_output = generate_answer(
            question,
            docs
        )

        test_case = LLMTestCase(
            input=question,
            actual_output=actual_output,
            expected_output=expected_answer,
            retrieval_context=retrieval_context,
        )

        test_cases.append(test_case)

    return test_cases


# ============================================================
# METRICS
# ============================================================

contextual_precision = ContextualPrecisionMetric(
    threshold=0.7,
    model=judge_model,
    include_reason=True,
)

contextual_recall = ContextualRecallMetric(
    threshold=0.7,
    model=judge_model,
    include_reason=True,
)

contextual_relevancy = ContextualRelevancyMetric(
    threshold=0.4,
    model=judge_model,
    include_reason=True,
)


# ============================================================
# RUN EVALUATION
# ============================================================

def evaluate_strategy(name, db):

    print("\n")
    print("=" * 80)
    print(f"TESTING: {name}")
    print("=" * 80)

    test_cases = create_test_cases(
        db,
        name
    )

    results = evaluate(
        test_cases=test_cases,
        metrics=[
            contextual_precision,
            contextual_recall,
            contextual_relevancy,
        ],
        async_config=AsyncConfig(run_async=False)
    )

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import os

    os.environ["DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE"] = "600"

    fixed_results = evaluate_strategy(
        "FIXED",
        fixed_db
    )

    semantic_results = evaluate_strategy(
        "SEMANTIC",
        semantic_db
    )

    hybrid_results = evaluate_strategy(
        "HYBRID",
        hybrid_db
    )