from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agents import (
    evaluate_candidate,
    critique_candidate
)

from app.scoring import calculate_overall_score

from app.database import save_candidate


class CandidateState(TypedDict, total=False):
    resume: dict
    job_description: str

    evaluation: object
    critic_result: object
    scores: dict

    retry_count: int
    max_retries: int

    error: str


def evaluate_node(state: CandidateState):

    try:

        evaluation = evaluate_candidate(
            resume_text=state["resume"]["text"],
            job_description=state["job_description"],
            critic_feedback=""
        )

        return {
            "evaluation": evaluation,
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def after_evaluate(state: CandidateState):

    if state.get("error"):

        return "error"

    if state.get("evaluation") is None:

        return "error"

    return "critic"


def critic_node(state: CandidateState):

    try:

        critic_result = critique_candidate(
            resume_text=state["resume"]["text"],
            evaluation=state["evaluation"]
        )

        return {
            "critic_result": critic_result,
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def should_retry(state: CandidateState):

    if state.get("error"):

        return "error"

    critic_result = state.get(
        "critic_result"
    )

    if critic_result is None:

        return "error"

    if critic_result.passed:

        return "score"

    retry_count = state.get(
        "retry_count",
        0
    )

    max_retries = state.get(
        "max_retries",
        1
    )

    if retry_count < max_retries:

        return "retry"

    return "error"


def retry_node(state: CandidateState):

    retry_count = state.get(
        "retry_count",
        0
    )

    return {
        "retry_count": retry_count + 1,
        "error": ""
    }


def retry_evaluate_node(state: CandidateState):

    try:

        critic_result = state.get(
            "critic_result"
        )

        feedback = ""

        if critic_result:

            feedback_parts = []

            if critic_result.explanation:

                feedback_parts.append(
                    critic_result.explanation
                )

            if critic_result.issues:

                feedback_parts.extend(
                    critic_result.issues
                )

            feedback = "\n".join(
                feedback_parts
            )

        evaluation = evaluate_candidate(
            resume_text=state["resume"]["text"],
            job_description=state["job_description"],
            critic_feedback=feedback
        )

        return {
            "evaluation": evaluation,
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def after_retry_evaluate(state: CandidateState):

    if state.get("error"):

        return "error"

    if state.get("evaluation") is None:

        return "error"

    return "critic"


def score_node(state: CandidateState):

    try:

        scores = calculate_overall_score(
            state["evaluation"]
        )

        return {
            "scores": scores,
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def store_node(state: CandidateState):

    try:

        save_candidate(
            resume=state["resume"],
            evaluation=state["evaluation"],
            scores=state["scores"]
        )

        return {
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def error_node(state: CandidateState):

    return {
        "error": state.get(
            "error",
            "Candidate processing failed."
        )
    }


def build_candidate_graph():

    graph = StateGraph(
        CandidateState
    )

    graph.add_node(
        "evaluate",
        evaluate_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    graph.add_node(
        "retry",
        retry_node
    )

    graph.add_node(
        "retry_evaluate",
        retry_evaluate_node
    )

    graph.add_node(
        "score",
        score_node
    )

    graph.add_node(
        "store",
        store_node
    )

    graph.add_node(
        "error",
        error_node
    )

    graph.add_edge(
        START,
        "evaluate"
    )

    graph.add_conditional_edges(
        "evaluate",
        after_evaluate,
        {
            "critic": "critic",
            "error": "error"
        }
    )

    graph.add_conditional_edges(
        "critic",
        should_retry,
        {
            "retry": "retry",
            "score": "score",
            "error": "error"
        }
    )

    graph.add_edge(
        "retry",
        "retry_evaluate"
    )

    graph.add_conditional_edges(
        "retry_evaluate",
        after_retry_evaluate,
        {
            "critic": "critic",
            "error": "error"
        }
    )

    graph.add_edge(
        "score",
        "store"
    )

    graph.add_edge(
        "store",
        END
    )

    graph.add_edge(
        "error",
        END
    )

    return graph.compile()