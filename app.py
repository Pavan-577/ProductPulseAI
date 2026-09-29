
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from utils.analysis import analyze_feedback
from utils.memory import store_feedback, recall_feedback


# ==========================================
# PDF REPORT GENERATOR
# ==========================================

def generate_pdf_report(comparison, memories=None):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph("ProductPulseAI", styles["Title"])
    )

    story.append(
        Paragraph(
            "AI-Powered Product Improvement Report",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 15))

    # Overall Summary
    improved = comparison[
        comparison["Status"] == "Improved"
    ]

    increased = comparison[
        comparison["Status"] == "Increased"
    ]

    unchanged = comparison[
        comparison["Status"] == "Unchanged"
    ]

    story.append(
        Paragraph("Overall Summary", styles["Heading1"])
    )

    summary_data = [
        ["Metric", "Count"],
        ["Issue Categories", str(len(comparison))],
        ["Issues Decreased", str(len(improved))],
        ["Issues Increased", str(len(increased))],
        ["Unchanged Issues", str(len(unchanged))],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[100 * mm, 55 * mm],
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    story.append(summary_table)
    story.append(Spacer(1, 18))

    # Old vs New Comparison
    story.append(
        Paragraph(
            "Old vs New Issue Comparison",
            styles["Heading1"],
        )
    )

    table_data = [
        ["Issue", "Previous", "Latest", "Difference", "Status"]
    ]

    for _, row in comparison.iterrows():
        table_data.append([
            escape(str(row["Issue"])),
            str(row["Previous Count"]),
            str(row["Latest Count"]),
            str(row["Difference"]),
            escape(str(row["Status"])),
        ])

    issue_table = Table(
        table_data,
        colWidths=[48 * mm, 25 * mm, 25 * mm, 25 * mm, 32 * mm],
        repeatRows=1,
    )

    issue_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    story.append(issue_table)
    story.append(Spacer(1, 18))

    # Historical Memory
    story.append(
        Paragraph(
            "Historical Feedback from Memory",
            styles["Heading1"],
        )
    )

    if memories:
        for memory in memories:
            story.append(
                Paragraph(
                    escape(str(memory)),
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 8))
    else:
        story.append(
            Paragraph(
                "No historical memories available.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 18))

    # Recommendations
    story.append(
        Paragraph(
            "Recommended Next Steps",
            styles["Heading1"],
        )
    )

    if not increased.empty:
        names = ", ".join(
            escape(str(x))
            for x in increased["Issue"].tolist()
        )

        story.append(
            Paragraph(
                f"Investigate the increase in: {names}. "
                "Review recent customer complaints and identify "
                "the reasons behind the increase.",
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 8))

    if not improved.empty:
        names = ", ".join(
            escape(str(x))
            for x in improved["Issue"].tolist()
        )

        story.append(
            Paragraph(
                f"Continue monitoring: {names}. "
                "Verify whether the reduction in complaints "
                "continues in future feedback.",
                styles["BodyText"],
            )
        )

    if not unchanged.empty:
        names = ", ".join(
            escape(str(x))
            for x in unchanged["Issue"].tolist()
        )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                f"Continue tracking unchanged issues: {names}.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "This report is based on feedback counts and retrieved "
            "memories. A decrease in complaints does not by itself "
            "prove that a product improvement caused the change.",
            styles["Italic"],
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="ProductPulse AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ProductPulse AI")

st.subheader(
    "Memory-Powered User Feedback Intelligence Agent"
)

st.write(
    "Analyze customer feedback, identify recurring issues, "
    "and track product improvements over time."
)


# ==========================================
# CSV UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Upload Customer Feedback CSV",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("data/sample_feedback.csv")

except Exception as e:
    st.error(f"Could not read CSV file: {e}")
    st.stop()


# ==========================================
# VALIDATE AND ANALYZE DATA
# ==========================================

if "feedback" not in df.columns:
    st.error("CSV must contain a 'feedback' column.")
    st.stop()

if df.empty:
    st.warning("The CSV contains no feedback.")
    st.stop()

try:
    df = analyze_feedback(df)

except Exception as e:
    st.error(f"Feedback analysis failed: {e}")
    st.stop()

if "sentiment" not in df.columns or "issue" not in df.columns:
    st.error(
        "Analysis must generate 'sentiment' and 'issue' columns."
    )
    st.stop()

st.success("Feedback analysis completed!")


# ==========================================
# SUMMARY METRICS
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric("Total Feedback", len(df))

col2.metric(
    "Positive Feedback",
    int((df["sentiment"] == "Positive").sum())
)

col3.metric(
    "Negative Feedback",
    int((df["sentiment"] == "Negative").sum())
)

st.divider()


# ==========================================
# SENTIMENT ANALYSIS
# ==========================================

st.subheader("📈 Sentiment Analysis")

sentiment_counts = (
    df["sentiment"].value_counts().reset_index()
)

sentiment_counts.columns = ["Sentiment", "Count"]

fig = px.pie(
    sentiment_counts,
    names="Sentiment",
    values="Count",
    title="Customer Sentiment Distribution",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)


# ==========================================
# CUSTOMER ISSUE ANALYSIS
# ==========================================

st.subheader("🔍 Customer Issues")

issue_counts = (
    df["issue"].value_counts().reset_index()
)

issue_counts.columns = ["Issue", "Count"]

fig2 = px.bar(
    issue_counts,
    x="Issue",
    y="Count",
    title="Most Reported Issues",
    color="Issue"
)

st.plotly_chart(fig2, use_container_width=True)


# ==========================================
# FEEDBACK DETAILS
# ==========================================

st.subheader("📋 Feedback Details")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()


# ==========================================
# HINDSIGHT MEMORY
# ==========================================

st.subheader("🧠 Hindsight Memory")

# Store feedback
if st.button("💾 Store Feedback in Memory"):

    try:
        for _, row in df.iterrows():

            store_feedback(
                str(row["feedback"]),
                metadata={
                    "customer_id": str(
                        row.get("customer_id", "Unknown")
                    ),
                    "issue": str(
                        row.get("issue", "Other")
                    ),
                    "product": str(
                        row.get("product", "Unknown")
                    )
                }
            )

        st.success(
            "Feedback stored successfully in Hindsight!"
        )

    except Exception as e:
        st.error(f"Memory storage failed: {e}")


# Recall previous feedback
query = st.text_input(
    "🔍 Search Previous Feedback",
    placeholder="Example: What delivery problems were reported?"
)

if st.button("Recall Memory"):

    if query.strip():

        try:
            result = recall_feedback(query)

            st.write("### 📝 Previous Feedback Memories")

            if result.results:
                for memory in result.results:
                    st.info(memory.text)
            else:
                st.warning("No matching memories found.")

        except Exception as e:
            st.error(f"Memory recall failed: {e}")

    else:
        st.warning("Please enter a search query.")


# ==========================================
# DOWNLOAD ANALYZED FEEDBACK
# ==========================================

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Analyzed Feedback",
    data=csv_data,
    file_name="analyzed_feedback.csv",
    mime="text/csv"
)


# ==========================================
# OLD VS NEW FEEDBACK COMPARISON
# ==========================================

st.divider()

st.header("📊 Old vs New Feedback Comparison")

st.write(
    "Compare customer issues across two time periods "
    "to identify improvements and unresolved problems."
)

# Initialize comparison safely
comparison = pd.DataFrame(
    columns=[
        "Issue",
        "Previous Count",
        "Latest Count",
        "Difference",
        "Status",
    ]
)

comparison_ready = False


if "date" not in df.columns:

    st.warning("CSV must contain a 'date' column.")

else:

    comparison_df = df.copy()

    comparison_df["date"] = pd.to_datetime(
        comparison_df["date"],
        errors="coerce"
    )

    comparison_df = comparison_df.dropna(
        subset=["date"]
    )

    available_dates = sorted(
        comparison_df["date"].dt.date.unique()
    )

    if len(available_dates) < 2:

        st.info(
            "At least two different dates are needed "
            "for comparison."
        )

    else:

        split_index = len(available_dates) // 2

        old_dates = available_dates[:split_index]
        new_dates = available_dates[split_index:]

        old_df = comparison_df[
            comparison_df["date"].dt.date.isin(old_dates)
        ]

        new_df = comparison_df[
            comparison_df["date"].dt.date.isin(new_dates)
        ]

        st.subheader("📅 Comparison Periods")

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"**Previous Feedback**\n\n"
                f"{old_dates[0]} to {old_dates[-1]}"
            )

        with col2:
            st.info(
                f"**Latest Feedback**\n\n"
                f"{new_dates[0]} to {new_dates[-1]}"
            )

        # Count issues
        old_counts = old_df["issue"].value_counts()
        new_counts = new_df["issue"].value_counts()

        all_issues = sorted(
            set(old_counts.index) | set(new_counts.index)
        )

        comparison = pd.DataFrame({
            "Issue": all_issues
        })

        comparison["Previous Count"] = (
            comparison["Issue"]
            .map(old_counts)
            .fillna(0)
            .astype(int)
        )

        comparison["Latest Count"] = (
            comparison["Issue"]
            .map(new_counts)
            .fillna(0)
            .astype(int)
        )

        comparison["Difference"] = (
            comparison["Latest Count"]
            - comparison["Previous Count"]
        )

        comparison["Status"] = comparison["Difference"].apply(
            lambda x: (
                "Improved" if x < 0
                else "Increased" if x > 0
                else "Unchanged"
            )
        )

        comparison_ready = True

        # Comparison table
        st.subheader("📈 Issue Comparison")

        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True
        )

        # Comparison chart
        fig3 = px.bar(
            comparison,
            x="Issue",
            y=["Previous Count", "Latest Count"],
            barmode="group",
            title="Previous vs Latest Issue Counts"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # Comparison summary
        st.subheader("💡 Comparison Summary")

        improved = comparison[
            comparison["Status"] == "Improved"
        ]

        increased = comparison[
            comparison["Status"] == "Increased"
        ]

        unchanged = comparison[
            comparison["Status"] == "Unchanged"
        ]

        c1, c2, c3 = st.columns(3)

        c1.metric("Issues Decreased", len(improved))
        c2.metric("Issues Increased", len(increased))
        c3.metric("Unchanged Issues", len(unchanged))

        if not improved.empty:
            st.success(
                "Issues with fewer reports: "
                + ", ".join(improved["Issue"].tolist())
            )

        if not increased.empty:
            st.warning(
                "Issues with more reports: "
                + ", ".join(increased["Issue"].tolist())
            )

        if not unchanged.empty:
            st.info(
                "Issues with unchanged counts: "
                + ", ".join(unchanged["Issue"].tolist())
            )


# ==========================================
# AI-POWERED IMPROVEMENT REPORT + PDF
# ==========================================

st.divider()

st.header("🧠 AI-Powered Improvement Report")

st.write(
    "Generate an automatic report using feedback comparison "
    "and relevant historical memories."
)

if not comparison_ready:

    st.info(
        "Upload feedback with at least two different dates "
        "to generate the improvement report."
    )


if st.button(
    "🚀 Generate Improvement Report",
    disabled=not comparison_ready
):

    st.subheader("📋 Product Improvement Report")

    # Identify issue trends
    improved_issues = comparison[
        comparison["Status"] == "Improved"
    ]

    increased_issues = comparison[
        comparison["Status"] == "Increased"
    ]

    unchanged_issues = comparison[
        comparison["Status"] == "Unchanged"
    ]

    # Overall summary
    st.markdown("### 📊 Overall Summary")

    st.write(
        f"Total issue categories analyzed: {len(comparison)}"
    )

    st.write(
        f"Issues with fewer reports: {len(improved_issues)}"
    )

    st.write(
        f"Issues with more reports: {len(increased_issues)}"
    )

    st.write(
        f"Issues with unchanged counts: {len(unchanged_issues)}"
    )

    # Improvement findings
    st.markdown("### ✅ Issues Showing Improvement")

    if not improved_issues.empty:

        for _, row in improved_issues.iterrows():

            st.success(
                f"{row['Issue']}: Reports decreased from "
                f"{row['Previous Count']} to {row['Latest Count']}."
            )

    else:
        st.info("No issues showed a decrease in reports.")

    # Issues requiring attention
    st.markdown("### ⚠️ Issues Requiring Attention")

    if not increased_issues.empty:

        for _, row in increased_issues.iterrows():

            st.warning(
                f"{row['Issue']}: Reports increased from "
                f"{row['Previous Count']} to {row['Latest Count']}."
            )

    else:
        st.success("No issue categories showed an increase.")

    # Unchanged issues
    st.markdown("### 🔄 Unchanged Issues")

    if not unchanged_issues.empty:

        for _, row in unchanged_issues.iterrows():

            st.info(
                f"{row['Issue']}: "
                f"{row['Latest Count']} reports in both periods."
            )

    else:
        st.write("No unchanged issue categories.")

    # Historical feedback
    st.markdown("### 🧠 Historical Feedback from Memory")

    memories = []

    try:

        memory_result = recall_feedback(
            "What previous customer complaints and issues "
            "were reported about delivery, tracking, "
            "food quality, and app experience?"
        )

        if memory_result.results:

            memories = [
                memory.text
                for memory in memory_result.results[:5]
            ]

            for memory in memories:
                st.info(memory)

        else:
            st.write("No matching historical memories found.")

    except Exception as e:

        st.warning(
            f"Could not retrieve historical memories: {e}"
        )

    # Recommended next steps
    st.markdown("### 💡 Recommended Next Steps")

    if not increased_issues.empty:

        issue_names = ", ".join(
            increased_issues["Issue"].astype(str).tolist()
        )

        st.write(
            f"Investigate the increase in: {issue_names}. "
            "Review recent customer complaints and identify "
            "the reasons behind the increase."
        )

    if not improved_issues.empty:

        issue_names = ", ".join(
            improved_issues["Issue"].astype(str).tolist()
        )

        st.write(
            f"Continue monitoring: {issue_names}. "
            "Verify whether the reduction in complaints "
            "continues in future feedback."
        )

    if not unchanged_issues.empty:

        issue_names = ", ".join(
            unchanged_issues["Issue"].astype(str).tolist()
        )

        st.write(
            f"Continue tracking unchanged issues: {issue_names}."
        )

    st.caption(
        "This report is based on feedback counts and retrieved "
        "memories. A decrease in complaints does not by itself "
        "prove that a product improvement caused the change."
    )

    # ==========================================
    # PDF DOWNLOAD
    # ==========================================

    st.divider()

    st.subheader("📄 Download Improvement Report")

    try:

        pdf_data = generate_pdf_report(
            comparison=comparison,
            memories=memories
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name="ProductPulse_Improvement_Report.pdf",
            mime="application/pdf",
            key="download_pdf_report"
        )

        st.success("PDF report generated successfully!")

    except Exception as e:

        st.error(f"PDF generation failed: {e}")