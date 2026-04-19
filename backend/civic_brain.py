import os
import operator
from typing import Annotated, List, TypedDict, Literal
import re

from dotenv import load_dotenv

# LangChain Imports
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchRun

# Tool Libraries
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# --- CONFIGURATION ---
load_dotenv() 

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("CRITICAL ERROR: GROQ_API_KEY not found in backend/.env")

try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key
    )
    print("--- [SYSTEM] Groq Scoring Engine Initialized ---")
except Exception as e:
    raise ValueError(f"Failed to initialize Groq AI: {e}")

# --- 1. STATE MANAGEMENT ---
class AgentState(TypedDict):
    request_id: str
    original_text: str
    party_name: str
    
    is_valid_manifesto: bool
    rejection_reason: str
    
    economist_report: str
    sociologist_report: str
    historical_context: List[str] 
    
    final_report: str
    chart_base64: str
    quality_score: int  # Feasibility Score
    trust_score: int    # Trust Score
    
    revision_count: int
    messages: Annotated[List[BaseMessage], operator.add]

# --- 2. TOOLS ---
@tool("internet_search", return_direct=False)
def search_tool(query: str):
    """Searches the web for verifying political claims."""
    print(f"   [TOOL] 🌍 SEARCHING WEB: {query}")
    try:
        search = DuckDuckGoSearchRun()
        if not query: return "Error: Empty search query."
        return search.invoke(query)[:1000]
    except Exception as e:
        print(f"   [SEARCH ERROR]: {e}")
        return "Search unavailable."

@tool("execute_plot_code", return_direct=False)
def code_execution_tool(data_points: str):
    """Takes 'Education:30,Defense:50' and runs Python code to generate a chart."""
    try:
        clean_data = data_points.replace("'", "").replace('"', "")
        items = clean_data.split(',')
        labels = []
        values = []
        for i in items:
            if ":" in i:
                parts = i.split(':')
                labels.append(parts[0].strip())
                val_str = ''.join(filter(str.isdigit, parts[1]))
                values.append(int(val_str) if val_str else 0)
        if not values: return "Error: No valid numbers."
        plt.figure(figsize=(6, 4))
        colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
        plt.bar(labels, values, color=colors)
        plt.title("Budget Allocation")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()
        return img_str
    except Exception as e:
        return f"Error generating chart: {e}"

tools = [search_tool, code_execution_tool]
llm_with_tools = llm.bind_tools(tools)

# --- 3. MEMORY ---
class MemoryBank:
    def query(self, text: str) -> str:
        return "Active."
memory_store = MemoryBank()

# --- 3b. TEXT HELPERS ---
def chunk_text(text: str, max_chars: int = 12000) -> str:
    """Truncate text to max_chars to stay within Groq token limits."""
    if len(text) <= max_chars:
        return text
    # Take first 10000 chars (party name + intro + key promises) and last 2000
    return text[:10000] + "\n\n[Document truncated for length...]\n\n" + text[-2000:]

def extract_party_name(text: str, llm) -> str:
    """Extract party name from the document."""
    try:
        res = llm.invoke(
            f"What is the name of the political party that wrote this document? "
            f"Reply with ONLY the party name, nothing else.\n\n{text[:3000]}"
        )
        return res.content.strip()
    except Exception:
        return "Unknown Party"

# --- 4. AGENTS ---

def orchestrator(state: AgentState):
    """
    THE BOUNCER: Checks if the document is actually a manifesto.
    """
    print(f"--- [ORCHESTRATOR] Scanning Document ---")
    prompt = ChatPromptTemplate.from_template(
        """You are a document classifier. Classify ONLY based on the text below.
        Do NOT invent content or use outside knowledge.

        Rules:
        - Resume / CV / Job Application -> REJECT
        - General Book / Novel -> REJECT
        - Political Manifesto / Party Platform / Policy Proposal / Election Document -> ACCEPT

        Document text (first 5000 characters):
        {text}

        Respond ONLY in this exact format:
        STATUS: [ACCEPT or REJECT]
        REASON: [One sentence based only on the text above]"""
    )
    try:
        res = llm.invoke(prompt.format(text=state['original_text'][:5000]))
        content = res.content
        if "STATUS: REJECT" in content:
            reason = content.split("REASON:")[1].strip() if "REASON:" in content else "Not a manifesto."
            return {
                "is_valid_manifesto": False, 
                "rejection_reason": f"### 🚫 Analysis Halted\n\n**Reason:** {reason}\n\n*Please upload a valid political manifesto.*"
            }
        party = extract_party_name(state['original_text'], llm)
        print(f"   [ORCHESTRATOR] Party identified: {party}")
        return {"is_valid_manifesto": True, "rejection_reason": "", "party_name": party}
    except Exception:
        return {"is_valid_manifesto": True, "rejection_reason": "", "party_name": "Unknown Party"}

def economist_agent(state: AgentState):
    if not state.get("is_valid_manifesto", True): return {"economist_report": "Skipped."}
    print("--- [AGENT A] Economist Extracting ---")
    prompt = ChatPromptTemplate.from_template(
        """You are an Expert Economist analysing the political manifesto of {party}.
        Read the document text below and extract ALL specific financial and economic promises made by {party}.
        Look for: taxes, wages, minimum wage, GDP targets, budget allocations, subsidies, loans, inflation targets, job creation numbers.
        List each promise clearly with any figures mentioned. Always refer to the party as {party}.
        If you find nothing relevant, say exactly what the document is about instead.

        Document text:
        {text}

        Economic Promises Found by {party}:"""
    )
    try:
        res = llm.invoke(prompt.format(
            text=chunk_text(state['original_text']),
            party=state.get('party_name', 'the party')
        ))
        return {"economist_report": str(res.content)}
    except Exception as e:
        print(f"Economist error: {e}")
        return {"economist_report": "Error reading text."}

def sociologist_agent(state: AgentState):
    if not state.get("is_valid_manifesto", True): return {"sociologist_report": "Skipped."}
    print("--- [AGENT B] Sociologist Extracting ---")
    prompt = ChatPromptTemplate.from_template(
        """You are a Sociologist analysing the political manifesto of {party}.
        Read the document text below and extract ALL social promises made by {party}.
        Look for: healthcare commitments, education policies, women rights, minority rights, caste/social justice, disability rights, safety, housing, food security.
        List each promise clearly with any targets or figures mentioned. Always refer to the party as {party}.
        If you find nothing relevant, say exactly what the document is about instead.

        Document text:
        {text}

        Social Promises Found by {party}:"""
    )
    try:
        res = llm.invoke(prompt.format(
            text=chunk_text(state['original_text']),
            party=state.get('party_name', 'the party')
        ))
        return {"sociologist_report": str(res.content)}
    except Exception as e:
        print(f"Sociologist error: {e}")
        return {"sociologist_report": "Error reading text."}

def memory_retrieval(state: AgentState):
    if not state.get("is_valid_manifesto", True): return {"historical_context": []}
    print("--- [HISTORY] Identifying Party ---")
    try:
        party_res = llm.invoke(f"Extract Political Party Name from: {state['original_text'][:5000]}")
        party_name = party_res.content.strip()
        
        query = f"political controversies and broken promises of {party_name}"
        data = search_tool.invoke({"query": query})
        return {"historical_context": [f"Search for {party_name}: {str(data)}"]}
    except Exception:
        return {"historical_context": ["History unavailable."]}

def skeptic_agent(state: AgentState):
    print("--- [AGENT C] Synthesizing & Scoring ---")
    
    # REJECTION HANDLING
    if not state.get("is_valid_manifesto", True):
        return {
            "final_report": state.get("rejection_reason"), 
            "quality_score": 0, 
            "trust_score": 0, 
            "chart_base64": None
        }

    try:
        history_str = "\n".join(state['historical_context'])
        
        party = state.get('party_name', 'the party')
        prompt = f"""You are a Voter Assistant analysing the manifesto of {party}.
        Use the party name "{party}" throughout your report — never say "the party" or "the document".
        Analyse ONLY the information provided below. Do NOT invent facts not present in the inputs.

        === ECONOMIST REPORT (about {party}) ===
        {state['economist_report']}

        === SOCIOLOGIST REPORT (about {party}) ===
        {state['sociologist_report']}

        === HISTORICAL CONTEXT (from web search about {party}) ===
        {history_str}

        === YOUR TASK ===
        Write a Markdown Voter Decision Guide for {party} with these sections:
        ## Executive Summary
        ## Economic Analysis
        ## Social Impact
        ## Risk Analysis

        Always name {party} explicitly in each section.
        Then on the final line, output scores in EXACTLY this format (two integers 0-100):
        SCORES: [Feasibility_Score], [Trust_Score]

        Feasibility Score: how realistic and funded the proposals appear (100 = very realistic, 0 = vague/unfunded)
        Trust Score: based on historical track record found above (100 = strong track record, 0 = history of broken promises)
        """
        
        res = llm.invoke(prompt)
        content = res.content
        
        # Extract Scores dynamically
        f_score = 0
        t_score = 0
        clean_report = content
        
        if "SCORES:" in content:
            parts = content.split("SCORES:")
            clean_report = parts[0].strip()
            score_line = parts[1].strip()
            # Regex to find numbers in "SCORES: 85, 40" or "SCORES: [85], [40]"
            nums = re.findall(r'\d+', score_line)
            if len(nums) >= 2:
                f_score = int(nums[0])
                t_score = int(nums[1])
        else:
            # Fallback if model forgets format, try to infer from text sentiment
            if "unrealistic" in content.lower() or "vague" in content.lower(): f_score = 40
            else: f_score = 80
            if "broken promise" in content.lower() or "scandal" in content.lower(): t_score = 30
            else: t_score = 85
        
        return {
            "final_report": clean_report, 
            "quality_score": f_score, 
            "trust_score": t_score, 
            "chart_base64": None
        }
    except Exception as e:
        print(f"Scoring Error: {e}")
        return {"final_report": "Summary failed.", "quality_score": 0, "trust_score": 0, "chart_base64": None}

def quality_gate(state: AgentState) -> Literal["orchestrator", "end"]:
    return "end"

# --- 5. GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("economist", economist_agent)
workflow.add_node("sociologist", sociologist_agent)
workflow.add_node("memory", memory_retrieval)
workflow.add_node("skeptic", skeptic_agent)

workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "economist")
workflow.add_edge("orchestrator", "sociologist")
workflow.add_edge("orchestrator", "memory")
workflow.add_edge("economist", "skeptic")
workflow.add_edge("sociologist", "skeptic")
workflow.add_edge("memory", "skeptic")
workflow.add_conditional_edges("skeptic", quality_gate, {"orchestrator": "orchestrator", "end": END})

checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)

def run_analysis_pipeline(thread_id: str, text: str):
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {
        "request_id": thread_id, 
        "original_text": text,
        "party_name": "",
        "revision_count": 0,
        "is_valid_manifesto": True,
        "rejection_reason": "",
        "economist_report": "",
        "sociologist_report": "",
        "historical_context": [],
        "final_report": "",
        "chart_base64": "",
        "quality_score": 0,
        "trust_score": 0,
        "messages": []
    }
    return app_graph.invoke(inputs, config=config)