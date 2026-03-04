import streamlit as st
import os
from dotenv import load_dotenv
from tools import ingest_source
from agent import WebAnalystAgent
from utils import generate_report_markdown, export_report
from eval import evaluate_action_items, compute_citation_coverage, compute_low_confidence_rate
import pandas as pd

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Web Content Analyst Agent", layout="wide")

# Initialize session state
if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
if 'sources' not in st.session_state:
    st.session_state.sources = []
if 'agent_log' not in st.session_state:
    st.session_state.agent_log = ""
if 'manual_texts' not in st.session_state:
    st.session_state.manual_texts = {}

st.title("🤖 Web Content Analyst Agent")
st.markdown("*Analyze web content with RAG, tool calling, and self-reflection*")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    
    if not api_key:
        st.warning("Please enter your OpenAI API key")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This agent:
    - Fetches YouTube transcripts & articles
    - Uses RAG with FAISS vector store
    - Performs self-reflection
    - Extracts structured insights
    """)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 Input", 
    "📄 Sources Preview", 
    "📊 Results", 
    "✅ Action Items",
    "📧 Email Draft",
    "📈 Evaluation",
    "🔍 Agent Log"
])

# Tab 1: Input
with tab1:
    st.header("Input Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        urls_input = st.text_area(
            "URLs (one per line)",
            height=150,
            placeholder="https://youtube.com/watch?v=...\nhttps://example.com/article"
        )
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["General summary", "Study notes", "Product/marketing analysis", "Technical tutorial extraction"]
        )
    
    with col2:
        tone = st.selectbox("Tone", ["Formal", "Friendly"])
        language = st.selectbox("Output Language", ["English", "Polish", "Ukrainian", "Russian"])
        
        st.markdown("---")
        
        if st.button("🚀 Run Agent", type="primary", disabled=not api_key):
            if not urls_input.strip():
                st.error("Please enter at least one URL")
            else:
                with st.spinner("Processing sources..."):
                    # Parse URLs
                    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
                    
                    # Ingest sources
                    sources = []
                    for url in urls:
                        manual_text = st.session_state.manual_texts.get(url, None)
                        source = ingest_source(url, manual_text)
                        sources.append(source)
                    
                    st.session_state.sources = sources
                    
                    # Load KB documents
                    kb_docs = []
                    kb_files = [
                        "kb/analysis_templates.md",
                        "kb/writing_style.md",
                        "kb/evaluation_rubric.md"
                    ]
                    for kb_file in kb_files:
                        if os.path.exists(kb_file):
                            with open(kb_file, 'r', encoding='utf-8') as f:
                                kb_docs.append((kb_file, f.read()))
                    
                    # Run agent
                    agent = WebAnalystAgent(api_key=api_key)
                    
                    try:
                        result = agent.run(
                            sources=[s for s in sources if s.content],
                            kb_docs=kb_docs,
                            analysis_mode=analysis_mode,
                            tone=tone.lower(),
                            language=language
                        )
                        
                        st.session_state.extraction_result = result
                        st.session_state.agent_log = agent.log.get_log()
                        
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")

# Tab 2: Sources Preview
with tab2:
    st.header("Sources Preview")
    
    if st.session_state.sources:
        for i, source in enumerate(st.session_state.sources):
            with st.expander(f"📄 {source.title}", expanded=False):
                st.markdown(f"**URL:** {source.url}")
                st.markdown(f"**Type:** {source.type}")
                st.markdown(f"**Length:** {source.length} characters")
                
                if source.error:
                    st.error(f"❌ Error: {source.error}")
                    
                    # Allow manual text input
                    manual_text = st.text_area(
                        "Paste content manually:",
                        key=f"manual_{i}",
                        height=150
                    )
                    if st.button(f"Save manual content", key=f"save_{i}"):
                        st.session_state.manual_texts[source.url] = manual_text
                        st.success("Manual content saved. Re-run the agent.")
                else:
                    st.text_area(
                        "Content Preview",
                        value=source.content[:1000] + "..." if len(source.content) > 1000 else source.content,
                        height=200,
                        disabled=True,
                        key=f"preview_{i}"
                    )
    else:
        st.info("No sources loaded yet. Go to Input tab and run the agent.")

# Tab 3: Results
with tab3:
    st.header("Analysis Results")
    
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        
        # Generate and display markdown report
        report_md = generate_report_markdown(result)
        st.markdown(report_md)
        
        # Export button
        if st.button("💾 Export Report"):
            os.makedirs("exports", exist_ok=True)
            filename = export_report(result, "exports/report.md")
            st.success(f"Report exported to {filename}")
            
            with open(filename, 'r', encoding='utf-8') as f:
                st.download_button(
                    "⬇️ Download Report",
                    f.read(),
                    file_name="report.md",
                    mime="text/markdown"
                )
    else:
        st.info("No results yet. Run the agent first.")

# Tab 4: Action Items
with tab4:
    st.header("Action Items Management")
    
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        
        # Collect all action items
        all_items = []
        for source in result.sources:
            for item in source.action_items:
                all_items.append({
                    "Source": source.title,
                    "Task": item.task,
                    "Owner": item.owner,
                    "Due Date": item.due_date,
                    "Priority": item.priority,
                    "Confidence": item.confidence,
                    "Quote": item.source_quote
                })
        
        if all_items:
            df = pd.DataFrame(all_items)
            
            # Highlight low confidence
            def highlight_low_conf(row):
                if row['Confidence'] < 0.55:
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_low_conf, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Action Items", len(all_items))
            with col2:
                low_conf = sum(1 for item in all_items if item['Confidence'] < 0.55)
                st.metric("Low Confidence Items", low_conf)
            with col3:
                avg_conf = sum(item['Confidence'] for item in all_items) / len(all_items)
                st.metric("Average Confidence", f"{avg_conf:.2f}")
            
            # Re-check button
            if st.button("🔄 Re-check Low Confidence Items"):
                st.info("Re-checking would trigger targeted re-retrieval and re-extraction (already done during reflection)")
        else:
            st.info("No action items extracted")
    else:
        st.info("No results yet. Run the agent first.")

# Tab 5: Email Draft
with tab5:
    st.header("Follow-up Email Draft")
    
    if st.session_state.extraction_result and api_key:
        result = st.session_state.extraction_result
        
        if st.button("✉️ Generate Email"):
            with st.spinner("Generating email..."):
                agent = WebAnalystAgent(api_key=api_key)
                email = agent.generate_email_draft(result, tone.lower())
                st.text_area("Email Draft", value=email, height=300)
    else:
        st.info("Run the agent first to generate email draft")

# Tab 6: Evaluation
with tab6:
    st.header("Evaluation Metrics")
    
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        
        # Collect all action items
        all_action_items = []
        for source in result.sources:
            all_action_items.extend(source.action_items)
        
        # Automatic metrics
        st.subheader("Automatic Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            citation_cov = compute_citation_coverage(all_action_items)
            st.metric("Citation Coverage", f"{citation_cov:.1%}")
            st.caption("% of action items with source quotes")
        
        with col2:
            low_conf_rate = compute_low_confidence_rate(all_action_items)
            st.metric("Low Confidence Rate", f"{low_conf_rate:.1%}")
            st.caption("% of action items with confidence < 0.55")
        
        st.markdown("---")
        
        # Manual evaluation
        st.subheader("Manual Evaluation")
        
        eval_method = st.radio("Evaluation Method", ["Checkbox-based", "Gold List"])
        
        if eval_method == "Checkbox-based":
            st.markdown("Mark correct action items:")
            
            correct_items = []
            for i, source in enumerate(result.sources):
                if source.action_items:
                    st.markdown(f"**{source.title}**")
                    for j, item in enumerate(source.action_items):
                        is_correct = st.checkbox(
                            f"{item.task} (conf: {item.confidence:.2f})",
                            key=f"eval_{i}_{j}"
                        )
                        if is_correct:
                            correct_items.append(item.task)
            
            if st.button("Calculate Metrics"):
                predicted = [item.task for source in result.sources for item in source.action_items]
                
                if correct_items:
                    precision = len(correct_items) / len(predicted) if predicted else 0
                    st.metric("Precision", f"{precision:.2%}")
                    st.caption(f"{len(correct_items)} correct out of {len(predicted)} predicted")
                else:
                    st.warning("No items marked as correct")
        
        else:  # Gold List
            gold_input = st.text_area(
                "Paste gold standard action items (one per line):",
                height=150
            )
            
            if st.button("Evaluate Against Gold"):
                if gold_input.strip():
                    gold_items = [line.strip() for line in gold_input.split('\n') if line.strip()]
                    predicted_items = [item.task for source in result.sources for item in source.action_items]
                    
                    precision, recall, f1, matches = evaluate_action_items(predicted_items, gold_items)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Precision", f"{precision:.2%}")
                    with col2:
                        st.metric("Recall", f"{recall:.2%}")
                    with col3:
                        st.metric("F1 Score", f"{f1:.2%}")
                    
                    if matches:
                        st.subheader("Matches")
                        for pred, gold, score in matches:
                            st.markdown(f"- **Predicted:** {pred}")
                            st.markdown(f"  **Gold:** {gold}")
                            st.markdown(f"  **Similarity:** {score:.2f}")
                else:
                    st.warning("Please enter gold standard items")
    else:
        st.info("No results yet. Run the agent first.")

# Tab 7: Agent Log
with tab7:
    st.header("Agent Execution Log")
    
    if st.session_state.agent_log:
        st.text_area("Log", value=st.session_state.agent_log, height=600, disabled=True)
    else:
        st.info("No log available. Run the agent first.")
