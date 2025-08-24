import streamlit as st
from utils import run_agent, generate_markdown_result


def main():
    st.title("⚖️ Compliance Check Agent")

    st.write(
        "Upload a **Part JSON** file and a **Regulation PDF** to run the compliance check."
    )

    part_file = st.file_uploader("Upload Part JSON", type=["json"])
    pdf_file = st.file_uploader("Upload Regulation PDF", type=["pdf"])

    if part_file and pdf_file:
        if st.button("Run Compliance Check"):
            with st.spinner("Running agent... please wait."):
                agent_state = run_agent(part_file, pdf_file)

                st.success("✅ Agent finished!")
                st.json(agent_state.model_dump())

                # Option to download agent JSON result
                result_json = agent_state.model_dump_json(indent=2)
                st.download_button(
                    label="📥 Download Result JSON",
                    data=result_json,
                    file_name="agent_state.json",
                    mime="application/json",
                )

            # Spinner for markdown generation
            with st.spinner("Generating markdown report..."):
                markdown_report = generate_markdown_result(agent_state)

                st.success("📝 Markdown report generated!")
                st.markdown(markdown_report)

                # Option to download the markdown report
                st.download_button(
                    label="📥 Download Report Markdown",
                    data=markdown_report,
                    file_name="compliance_report.md",
                    mime="text/markdown",
                )


if __name__ == "__main__":
    main()
