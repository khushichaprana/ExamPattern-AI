import pandas as pd
import streamlit as st

# set_page_config must be the first Streamlit command
st.set_page_config(
    page_title="ExamPredict AI",
    page_icon="📚",
    layout="wide",
)

# =====================================================================
# DATA FORMAT (read this before editing)
# ---------------------------------------------------------------------
# Each subject has:
#   units : {unit name: [topics]}            (from the syllabus)
#   pyq   : [(year, question no, question, "topic1;topic2", marks), ...]
# A topic name in pyq must match a topic in units EXACTLY.
# To add a new paper: add more rows to that subject's pyq list.
# Topics marked "(from papers)" were asked in papers but are not listed
# separately in the syllabus, so they were added.
# =====================================================================

# ---------------------------------------------------------------------
# 1. JAVA PROGRAMMING (BCG-301-V)
# ---------------------------------------------------------------------
JAVA_UNITS = {
    "Unit 1: Java Language Basics": [
        "Introduction to Java",
        "Basic Features of Java",
        "Java Virtual Machine (JVM)",
        "Primitive Data Types and Variables",
        "Java Operators",
        "Expressions and Statements",
        "Arrays",
        "String Class",  # (from papers)
    ],
    "Unit 2: Classes, Inheritance and Polymorphism": [
        "Classes and Objects",
        "Array of Objects",
        "Objects as Function Arguments",
        "Scope Resolution Operator",
        "Static Data Members",
        "Inheritance and its Types",
        "Constructors and their Types",
        "Polymorphism",
        "Abstract Class",
        "Interface and Packages",
        "Encapsulation and Data Hiding",  # (from papers)
        "Final Keyword",  # (from papers)
    ],
    "Unit 3: Exceptions and Multithreading": [
        "Exception Handling",
        "Try and Catch Blocks",
        "Throw and Throws",
        "Multiple Catch Blocks",
        "User Defined Exceptions",
        "Process and Thread",
        "Life Cycle of a Thread",
        "Thread Creation",
        "Thread Priority",
        "Synchronization",
        "Producer Consumer Problem",
    ],
    "Unit 4: I/O in Java": [
        "I/O Basics",
        "Types of Streams",
        "Stream Classes",
        "Predefined Streams",
        "Reading and Writing to Console",
        "Reading and Writing Files",
        "Object Serialization",
    ],
}

JAVA_PYQ = [
    # ---- December 2023 ----
    (2023, "Q1(a)", "How is data hiding implemented in Java?", "Encapsulation and Data Hiding", 1.5),
    (2023, "Q1(b)", "Differentiate between compiler and interpreter", "Introduction to Java", 1.5),
    (2023, "Q1(c)", "Purpose of garbage collector", "Java Virtual Machine (JVM)", 1.5),
    (2023, "Q1(d)", "Explain final, finally, finalize", "Final Keyword", 1.5),
    (2023, "Q1(e)", "Significance of public static void main(String a[])", "Introduction to Java", 1.5),
    (2023, "Q1(f)", "How do we set CLASSPATH?", "Interface and Packages", 1.5),
    (2023, "Q1(g)", "Define different types of exceptions", "Exception Handling", 1.5),
    (2023, "Q1(h)", "What does JVM do when an exception occurs?", "Exception Handling", 1.5),
    (2023, "Q1(i)", "Benefits of multi-threaded programming", "Process and Thread", 1.5),
    (2023, "Q1(j)", "What are volatile modifiers in Java?", "Synchronization", 1.5),
    (2023, "Q2(a)", "Abstract classes vs interfaces with example", "Abstract Class;Interface and Packages", 10),
    (2023, "Q2(b)", "Explain this pointer with example", "Classes and Objects", 5),
    (2023, "Q3(a)", "Program to count words from a text file using stream classes", "Stream Classes;Reading and Writing Files", 5),
    (2023, "Q3(b)", "Function overloading with example", "Polymorphism", 10),
    (2023, "Q4", "Inheritance and its types; implement Device/Loader/Mobile", "Inheritance and its Types;Interface and Packages", 15),
    (2023, "Q5(a)", "Program to create package Math_s (addition, subtraction)", "Interface and Packages", 5),
    (2023, "Q5(b)", "Exception handling with try, catch, throw, throws program", "Exception Handling;Try and Catch Blocks;Throw and Throws", 10),
    (2023, "Q6", "Create a thread, thread states, odd/even threads program", "Thread Creation;Life Cycle of a Thread", 15),
    (2023, "Q7(i)", "Short note: String class", "String Class", 5),
    (2023, "Q7(ii)", "Short note: Packages", "Interface and Packages", 5),
    (2023, "Q7(iii)", "Short note: Function overriding", "Polymorphism", 5),
    (2023, "Q7(iv)", "Short note: Encapsulation", "Encapsulation and Data Hiding", 5),
    # ---- December 2025 ----
    (2025, "Q1(a)", "Is Java purely object oriented? Justify", "Introduction to Java", 1.5),
    (2025, "Q1(b)", "Difference between class and object", "Classes and Objects", 1.5),
    (2025, "Q1(c)", "Difference between constructor and method", "Constructors and their Types", 1.5),
    (2025, "Q1(d)", "Difference between abstract class and interface", "Abstract Class;Interface and Packages", 1.5),
    (2025, "Q1(e)", "Why do we declare a class final?", "Final Keyword", 1.5),
    (2025, "Q1(f)", "Containership vs inheritance", "Inheritance and its Types", 1.5),
    (2025, "Q1(g)", "What is a Unicode system?", "Primitive Data Types and Variables", 1.5),
    (2025, "Q1(h)", "What are static methods?", "Static Data Members", 1.5),
    (2025, "Q1(i)", "What are operators in Java?", "Java Operators", 1.5),
    (2025, "Q1(j)", "extends Thread vs implements Runnable", "Thread Creation", 1.5),
    (2025, "Q2(a)", "Need of JVM; architecture of JVM", "Java Virtual Machine (JVM)", 8),
    (2025, "Q2(b)", "Constructor and its types with examples", "Constructors and their Types", 7),
    (2025, "Q3(a)", "Multithreading significance; thread life cycle", "Process and Thread;Life Cycle of a Thread", 8),
    (2025, "Q3(b)", "Stream; program to read keyboard and write myfile.txt", "I/O Basics;Reading and Writing to Console;Reading and Writing Files", 7),
    (2025, "Q4(a)", "Inheritance and its types with examples", "Inheritance and its Types", 9),
    (2025, "Q4(b)", "Object serialization; serialization program", "Object Serialization", 6),
    (2025, "Q5(a)", "Package, types of packages, Addition class program", "Interface and Packages", 8),
    (2025, "Q5(b)", "Exception, common types, how to deal with it", "Exception Handling", 7),
    (2025, "Q6(a)", "Interface; multiple inheritance using interfaces", "Interface and Packages;Inheritance and its Types", 8),
    (2025, "Q6(b)", "Thread synchronization; synchronized block program", "Synchronization", 7),
    (2025, "Q7(a)", "Short note: Types of streams", "Types of Streams", 5),
    (2025, "Q7(b)", "Short note: Objects as method arguments", "Objects as Function Arguments", 5),
    (2025, "Q7(c)", "Short note: Features of Java", "Basic Features of Java", 5),
]

# ---------------------------------------------------------------------
# 2. MACHINE LEARNING-1 (BCG-321-V)
# ---------------------------------------------------------------------
ML_UNITS = {
    "Unit 1: Introduction of Machine Learning": [
        "ML Basic Concepts",
        "Perspectives and Issues in ML",
        "Types of ML (Supervised Unsupervised Reinforcement)",
        "Data Representations",
        "Applications of ML",
        "Bias-Variance and Overfitting",  # (from papers)
        "Data Preprocessing and Feature Engineering",  # (from papers)
    ],
    "Unit 2: Supervised Learning (Regression/Classification)": [
        "Linear Regression",
        "Logistic Regression",
        "Nearest Neighbours (KNN)",
        "Decision Trees",
        "Support Vector Machines",
        "Nonlinearity and Kernel Methods",
    ],
    "Unit 3: Unsupervised Learning": [
        "K-means and Kernel K-means",
        "Dimensionality Reduction (PCA)",
        "Matrix Factorization and Matrix Completion",
        "Separating Hyperplanes (RPL Algorithm)",
        "Optimal Separating Hyperplane",
    ],
    "Unit 4: Techniques and Applications": [
        "Scalable Machine Learning",
        "Naive Bayes",
        "Bayesian Learning and Inference",
        "Recent Trends in ML",
        "Model Evaluation Metrics",  # (from papers)
    ],
}

ML_PYQ = [
    (2025, "Q1(a)", "Learning from data; bias-variance tradeoff", "ML Basic Concepts;Bias-Variance and Overfitting", 1.5),
    (2025, "Q1(b)", "Linear Regression vs Logistic Regression", "Linear Regression;Logistic Regression", 1.5),
    (2025, "Q1(c)", "Key concept of singular value decomposition", "Matrix Factorization and Matrix Completion", 1.5),
    (2025, "Q1(d)", "Importance of data preprocessing in ML pipeline", "Data Preprocessing and Feature Engineering", 1.5),
    (2025, "Q1(e)", "Write the algorithm of KNN", "Nearest Neighbours (KNN)", 1.5),
    (2025, "Q1(f)", "Role of regularization in Matrix Factorization", "Matrix Factorization and Matrix Completion", 1.5),
    (2025, "Q1(g)", "Fill in the blanks (SVM line, logistic function, KNN tie)", "Support Vector Machines;Logistic Regression;Nearest Neighbours (KNN)", 1.5),
    (2025, "Q1(h)", "True/False (SVM hyperplane, linear regression, KNN k value)", "Support Vector Machines;Linear Regression;Nearest Neighbours (KNN)", 1.5),
    (2025, "Q1(i)", "Feature engineering; how it is done in deep learning", "Data Preprocessing and Feature Engineering", 1.5),
    (2025, "Q1(j)", "Overfitting with example", "Bias-Variance and Overfitting", 1.5),
    (2025, "Q2(a)", "How soft margin SVM handles outliers and overlapping classes", "Support Vector Machines", 10),
    (2025, "Q2(b)", "Data representation: numerical, categorical, graph-based", "Data Representations", 5),
    (2025, "Q3(a)", "Role of kernel trick for non-linear problems", "Nonlinearity and Kernel Methods", 10),
    (2025, "Q3(b)", "Decision Trees; construction using Entropy and Information Gain", "Decision Trees", 5),
    (2025, "Q4", "Numerical: reduce 2 dimensions to 1 using PCA", "Dimensionality Reduction (PCA)", 15),
    (2025, "Q5(a)", "Challenges of large datasets; scalability in modern ML", "Scalable Machine Learning", 10),
    (2025, "Q5(b)", "How Naive Bayes performs classification", "Naive Bayes", 5),
    (2025, "Q6(a)", "Recent trends: deep learning, reinforcement learning", "Recent Trends in ML", 10),
    (2025, "Q6(b)", "Importance of Bayesian Inference in probabilistic models", "Bayesian Learning and Inference", 5),
    (2025, "Q7(a)", "Error evaluation metrics in ML", "Model Evaluation Metrics", 5),
    (2025, "Q7(b)", "Short note: Federated learning", "Recent Trends in ML", 5),
    (2025, "Q7(c)", "RPL algorithm for dimensionality reduction and generalization", "Separating Hyperplanes (RPL Algorithm)", 5),
]

# ---------------------------------------------------------------------
# 3. SPEECH AND AUDIO PROCESSING (BCG-307-V)
# ---------------------------------------------------------------------
SAP_UNITS = {
    "Unit 1: Introduction and Speech Signal Processing": [
        "Speech Production and Modelling",
        "Human Auditory System",
        "General Structure of Speech Coders",
        "Classification of Speech Coding Techniques",
        "Requirements of Speech Codecs",
        "Pitch-Period Estimation",
        "All-pole and All-zero Filters",
        "Convolution",
        "Power Spectral Density and Periodogram",
        "Autoregressive Model",
        "Autocorrelation Estimation",
    ],
    "Unit 2: Linear Prediction of Speech and Speech Quantization": [
        "Basic Concepts of Linear Prediction",
        "LP Analysis of Non-stationary Signals",
        "Levinson-Durbin Algorithm",
        "Long-term and Short-term Linear Prediction",
        "Moving Average Prediction",
        "Scalar Quantization",
        "Vector Quantization",
    ],
    "Unit 3: Scalar Quantization of LPC and Linear Prediction Coding": [
        "Spectral Distortion Measures",
        "Reflection Coefficient and Log Area Ratio Quantization",
        "Line Spectral Frequency (LSF)",
        "LPC Model of Speech Production",
        "Structures of LPC Encoders and Decoders",
        "Voicing Detection",
        "Limitations of the LPC Model",
    ],
    "Unit 4: Code Excited Linear Prediction": [
        "CELP Speech Production Model",
        "Analysis-by-Synthesis",
        "Generic CELP Encoders and Decoders",
        "Excitation Codebook Search",
        "CELP with Adaptive Codebook",
        "Low Delay CELP",
        "Algebraic CELP",
        "Speech Coding Standards",
    ],
}

SAP_PYQ = [
    (2025, "Q1(a)", "Parts of the human auditory system", "Human Auditory System", 1.5),
    (2025, "Q1(b)", "Speech codec requirements", "Requirements of Speech Codecs", 1.5),
    (2025, "Q1(c)", "What is G.711?", "Speech Coding Standards", 1.5),
    (2025, "Q1(d)", "Non-stationary signal with example", "LP Analysis of Non-stationary Signals", 1.5),
    (2025, "Q1(e)", "Role of a quantizer", "Scalar Quantization", 1.5),
    (2025, "Q1(f)", "What does moving average prediction do?", "Moving Average Prediction", 1.5),
    (2025, "Q1(g)", "Meaning of LSFs", "Line Spectral Frequency (LSF)", 1.5),
    (2025, "Q1(h)", "What is a vocal tract filter?", "Speech Production and Modelling", 1.5),
    (2025, "Q1(i)", "What is a CELP encoder?", "Generic CELP Encoders and Decoders", 1.5),
    (2025, "Q1(j)", "Example of a speech coding standard", "Speech Coding Standards", 1.5),
    (2025, "Q2(a)", "Waveform coders vs parametric coders", "Classification of Speech Coding Techniques", 7.5),
    (2025, "Q2(b)", "Diagram of Human Auditory System with labels", "Human Auditory System", 7.5),
    (2025, "Q3(a)", "Pitch and pitch period; pitch estimation methods", "Pitch-Period Estimation", 7.5),
    (2025, "Q3(b)", "Challenges of standard LPC for non-stationary signals", "LP Analysis of Non-stationary Signals", 7.5),
    (2025, "Q4(a)", "Applications of Levinson-Durbin algorithm", "Levinson-Durbin Algorithm", 7.5),
    (2025, "Q4(b)", "Logarithmic quantizer and its benefits", "Scalar Quantization", 7.5),
    (2025, "Q5(a)", "LPC to LSF conversions", "Line Spectral Frequency (LSF)", 7.5),
    (2025, "Q5(b)", "Limitations of the LPC model", "Limitations of the LPC Model", 7.5),
    (2025, "Q6(a)", "Diagram of LPC encoder; explain each block", "Structures of LPC Encoders and Decoders", 7.5),
    (2025, "Q6(b)", "Purpose of Zero Input (ZI) and Zero State (ZS) decomposition", "Excitation Codebook Search", 7.5),
    (2025, "Q7(a)", "Low delay CELP vs conventional CELP", "Low Delay CELP", 7.5),
    (2025, "Q7(b)", "Main components of CELP decoder; how decoding works", "Generic CELP Encoders and Decoders", 7.5),
]

# ---------------------------------------------------------------------
# 4. ANALYSIS OF DESIGN AND ALGORITHMS (BCG-305-V)
# ---------------------------------------------------------------------
ADA_UNITS = {
    "Unit 1: Introduction and Divide and Conquer": [
        "Basic Characteristics of Algorithms",
        "Empirical and Analytical Analysis",
        "Complexity and Asymptotic Notations",
        "Binary and Ternary Search",
        "Merge Sort",
        "Quick Sort",
        "Selection",
        "Strassen's Matrix Multiplication",
        "Recursion",  # (from papers)
        "Stable Sorting",  # (from papers)
    ],
    "Unit 2: Greedy Methods": [
        "Greedy Method General",
        "Knapsack Problem",
        "Job Sequencing with Deadlines",
        "Minimum Spanning Trees",
        "Single Source Shortest Paths (Greedy)",
        "Travelling Salesman Problem (Greedy)",
        "Optimal Storage on Tapes",
        "Optimal Merge Patterns",
    ],
    "Unit 3: Dynamic Programming": [
        "Dynamic Programming General Method",
        "Single Source Shortest Path (DP)",
        "All Pair Shortest Path",
        "Optimal Binary Search Trees",
        "0/1 Knapsack",
        "Travelling Salesman Problem (DP)",
    ],
    "Unit 4: Back Tracking": [
        "General Method of Backtracking",
        "8 Queen's Problem",
        "Graph Coloring",
        "Sum of Subsets",
        "Hamiltonian Cycles",
        "Deterministic and Non-deterministic Algorithms",  # (from papers)
        "P NP-Hard and NP-Complete",  # (from papers)
        "Least Cost Search (Branch and Bound)",  # (from papers)
    ],
}

ADA_PYQ = [
    (2025, "Q1(a)", "Divide & Conquer vs Dynamic Programming", "Dynamic Programming General Method", 1.5),
    (2025, "Q1(b)", "Order functions by asymptotic complexity", "Complexity and Asymptotic Notations", 1.5),
    (2025, "Q1(c)", "Why Greedy is not suggested for 0/1 Knapsack", "Knapsack Problem;0/1 Knapsack", 1.5),
    (2025, "Q1(d)", "Does Bellman-Ford always find negative cycle?", "Single Source Shortest Path (DP)", 1.5),
    (2025, "Q1(e)", "When is a sorting technique stable? 2 examples", "Stable Sorting", 1.5),
    (2025, "Q1(f)", "Implicit and explicit constraints in backtracking", "General Method of Backtracking", 1.5),
    (2025, "Q1(g)", "Significance of asymptotic notations", "Complexity and Asymptotic Notations", 1.5),
    (2025, "Q1(h)", "Deterministic vs non-deterministic algorithms", "Deterministic and Non-deterministic Algorithms", 1.5),
    (2025, "Q1(i)", "Least Cost Search function in brief", "Least Cost Search (Branch and Bound)", 1.5),
    (2025, "Q1(j)", "Differentiate P, NP-Hard and NP-Complete", "P NP-Hard and NP-Complete", 1.5),
    (2025, "Q2(a)", "Algorithm for non-recursive binary search", "Binary and Ternary Search", 5),
    (2025, "Q2(b)", "Merge sort algorithm and its complexity", "Merge Sort", 10),
    (2025, "Q3(a)", "Recursion for Fibonacci series", "Recursion", 5),
    (2025, "Q3(b)", "Strassen's matrix multiplication; derive time complexity", "Strassen's Matrix Multiplication", 10),
    (2025, "Q4(a)", "Job sequencing with deadlines (numerical)", "Job Sequencing with Deadlines", 9),
    (2025, "Q4(b)", "Travelling salesman optimal route (cost matrix)", "Travelling Salesman Problem (DP)", 6),
    (2025, "Q5(a)", "Shortest path A to F using greedy method", "Single Source Shortest Paths (Greedy)", 5),
    (2025, "Q5(b)", "Optimal storage on tapes", "Optimal Storage on Tapes", 10),
    (2025, "Q6(a)", "Backtracking vs DP; N-Queen problem", "General Method of Backtracking;Dynamic Programming General Method;8 Queen's Problem", 9),
    (2025, "Q6(b)", "Optimal merge patterns with example", "Optimal Merge Patterns", 6),
    (2025, "Q7(a)", "Short note: Hamiltonian cycle", "Hamiltonian Cycles", 8),
    (2025, "Q7(b)", "Short note: Graph colouring problem", "Graph Coloring", 7),
]

# ---------------------------------------------------------------------
# 5. SOFTWARE ENGINEERING (BCG-303-V)
# ---------------------------------------------------------------------
SE_UNITS = {
    "Unit 1: Introduction and Software Requirement": [
        "Software Processes and Characteristics",
        "Waterfall Model",
        "Prototype Model",
        "Evolutionary Model",
        "Spiral Model",
        "Requirement Elicitation (FAST QFD)",
        "Requirements Analysis (DFD)",
        "Data Dictionaries and ER Diagrams",
        "Requirements Documentation and SRS",
    ],
    "Unit 2: Project Management and Project Planning": [
        "Management Spectrum",
        "Size Estimation (LOC and Function Count)",
        "Cost Estimation Models (COCOMO)",
        "McCabe Cyclomatic Complexity",
        "Risk Management",
    ],
    "Unit 3: Software Design": [
        "Cohesion and Coupling",
        "Function Oriented Design",
        "Object Oriented Design",
        "Software Metrics and Measurement",
        "Token Count",
        "Halstead Software Science Measures",
        "Design Metrics",
        "Data Structure Metrics",
    ],
    "Unit 4: Software Testing": [
        "Testing Process",
        "Design of Test Cases",
        "Functional Testing",
        "Structural Testing",
        "Test Activities",
        "Unit Testing",
        "Integration Testing",
        "System Testing",
        "Debugging Activities",
    ],
}

SE_PYQ = [
    (2025, "Q1(a)", "Objective of software engineering", "Software Processes and Characteristics", 1.5),
    (2025, "Q1(b)", "What is a test case?", "Design of Test Cases", 1.5),
    (2025, "Q1(c)", "What is object-oriented design?", "Object Oriented Design", 1.5),
    (2025, "Q1(d)", "Relation between design and implementation", "Function Oriented Design", 1.5),
    (2025, "Q1(e)", "What is a Data Dictionary?", "Data Dictionaries and ER Diagrams", 1.5),
    (2025, "Q1(f)", "Advantages of the spiral model", "Spiral Model", 1.5),
    (2025, "Q1(g)", "Why software measurement is essential for QA", "Software Metrics and Measurement", 1.5),
    (2025, "Q1(h)", "What is unit testing? Why important?", "Unit Testing", 1.5),
    (2025, "Q1(i)", "Why people are the most important project resource", "Management Spectrum", 1.5),
    (2025, "Q1(j)", "Purpose of preparing an SRS", "Requirements Documentation and SRS", 1.5),
    (2025, "Q2(a)", "Waterfall life cycle model and its working", "Waterfall Model", 7),
    (2025, "Q2(b)", "Requirement elicitation; QFD technique", "Requirement Elicitation (FAST QFD)", 8),
    (2025, "Q3(a)", "Factors affecting software cost; basic COCOMO", "Cost Estimation Models (COCOMO)", 8),
    (2025, "Q3(b)", "Data structure metrics; amount of data in a program", "Data Structure Metrics", 7),
    (2025, "Q4(a)", "Coupling vs cohesion; types of coupling", "Cohesion and Coupling", 8),
    (2025, "Q4(b)", "McCabe's cyclomatic complexity", "McCabe Cyclomatic Complexity", 7),
    (2025, "Q5(a)", "Integration testing and its process", "Integration Testing", 7),
    (2025, "Q5(b)", "Structural testing; purpose and importance", "Structural Testing", 8),
    (2025, "Q6(a)", "System testing and overall requirements", "System Testing", 8),
    (2025, "Q6(b)", "Function count vs LOC; size and effort estimation", "Size Estimation (LOC and Function Count)", 7),
    (2025, "Q7(a)", "Short note: Risk Management", "Risk Management", 5),
    (2025, "Q7(b)", "Short note: Debugging Activities", "Debugging Activities", 5),
    (2025, "Q7(c)", "Short note: Halstead Software Science Measures", "Halstead Software Science Measures", 5),
]

# =====================================================================
# ALL SUBJECTS
# =====================================================================
SUBJECTS = {
    "Java Programming": {"code": "BCG-301-V", "units": JAVA_UNITS, "pyq": JAVA_PYQ},
    "Machine Learning-1": {"code": "BCG-321-V", "units": ML_UNITS, "pyq": ML_PYQ},
    "Speech and Audio Processing": {"code": "BCG-307-V", "units": SAP_UNITS, "pyq": SAP_PYQ},
    "Analysis of Design and Algorithms": {"code": "BCG-305-V", "units": ADA_UNITS, "pyq": ADA_PYQ},
    "Software Engineering": {"code": "BCG-303-V", "units": SE_UNITS, "pyq": SE_PYQ},
}

PRIORITY_ICON = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "Not asked yet": "⚪"}


# =====================================================================
# ANALYSIS
# =====================================================================
def topic_to_unit_map(info):
    return {t: u for u, ts in info["units"].items() for t in ts}


def build_question_table(info):
    """One row per (question, topic)."""
    mapping = topic_to_unit_map(info)
    rows = []
    for year, qno, question, topics, marks in info["pyq"]:
        part = "A" if qno.startswith("Q1") else "B"
        for topic in topics.split(";"):
            topic = topic.strip()
            rows.append(
                {
                    "Year": year,
                    "Part": part,
                    "Q.No": qno,
                    "Question": question,
                    "Topic": topic,
                    "Unit": mapping.get(topic, "UNKNOWN"),
                    "Marks": marks,
                }
            )
    return pd.DataFrame(rows)


def priority_label(papers, score, total_papers, high_cut, mid_cut, top_score):
    """Priority is relative to the other asked topics of the same subject."""
    if score <= 0:
        return "Not asked yet"
    if score > high_cut or score >= top_score:
        return "High"  # top ~25% of asked topics
    if score >= mid_cut or (total_papers > 1 and papers == total_papers):
        return "Medium"  # middle group, or repeated in every paper
    return "Low"


def build_topic_stats(df, info):
    """Score every syllabus topic. Latest paper counts 1.5x (recency)."""
    mapping = topic_to_unit_map(info)
    latest = df["Year"].max()
    total_papers = df["Year"].nunique()

    work = df.copy()
    work["Weighted"] = work.apply(
        lambda r: r["Marks"] * (1.5 if r["Year"] == latest else 1.0), axis=1
    )

    grouped = (
        work.groupby("Topic")
        .agg(
            Times_Asked=("Question", "count"),
            Papers=("Year", "nunique"),
            Total_Marks=("Marks", "sum"),
            Score=("Weighted", "sum"),
        )
        .reset_index()
    )

    base = pd.DataFrame({"Topic": list(mapping.keys()), "Unit": list(mapping.values())})
    stats = base.merge(grouped, on="Topic", how="left")
    for col in ["Times_Asked", "Papers", "Total_Marks", "Score"]:
        stats[col] = stats[col].fillna(0)
    stats["Times_Asked"] = stats["Times_Asked"].astype(int)
    stats["Papers"] = stats["Papers"].astype(int)

    asked = stats.loc[stats["Score"] > 0, "Score"]
    high_cut = asked.quantile(0.75) if len(asked) > 0 else 0
    mid_cut = asked.quantile(0.40) if len(asked) > 0 else 0
    top_score = asked.max() if len(asked) > 0 else 0

    stats["Priority"] = [
        priority_label(p, sc, total_papers, high_cut, mid_cut, top_score)
        for p, sc in zip(stats["Papers"], stats["Score"])
    ]
    return stats


def build_overview():
    rows = []
    for name, info in SUBJECTS.items():
        d = build_question_table(info)
        s = build_topic_stats(d, info)
        top3 = (
            s[s["Score"] > 0].sort_values("Score", ascending=False).head(3)["Topic"].tolist()
        )
        rows.append(
            {
                "Subject": name,
                "Code": info["code"],
                "Papers": d["Year"].nunique(),
                "Questions": len(info["pyq"]),
                "Top 3 Topics": ", ".join(top3),
            }
        )
    return pd.DataFrame(rows)


# =====================================================================
# UI
# =====================================================================
st.title("📚 ExamPredict AI")
st.subheader("Smart Exam Preparation and Topic Analysis")

subject = st.selectbox("📘 Select Subject", list(SUBJECTS.keys()))
info = SUBJECTS[subject]
UNITS = info["units"]

df = build_question_table(info)
stats = build_topic_stats(df, info)
paper_years = sorted(df["Year"].unique())
paper_text = ", ".join(f"Dec {y}" for y in paper_years)

st.info(
    f"Prediction for {subject} is based on previous-year papers ({paper_text}). "
    "Topics with more marks, repeated across papers and asked in the latest paper "
    "get a higher score."
)

if len(paper_years) == 1:
    st.warning(
        "Only 1 paper is available for this subject, so this is an indicative "
        "prediction. Adding more papers will make it more accurate."
    )

unknown = df[df["Unit"] == "UNKNOWN"]["Topic"].unique()
if len(unknown) > 0:
    st.error(
        "These topics in the PYQ data are not in the syllabus list, "
        "please fix the spelling: " + ", ".join(unknown)
    )

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Subject Code", info["code"])
c2.metric("Semester", "BCA - V")
c3.metric("Total Units", len(UNITS))
c4.metric("Papers Analysed", len(paper_years))
c5.metric("Questions Analysed", len(info["pyq"]))

st.markdown("---")

tab_top, tab_unit, tab_search, tab_data, tab_all = st.tabs(
    ["🔥 Top Topics", "📊 Unit-wise", "🔍 Find a Topic", "🗂️ Paper Data", "🏠 All Subjects"]
)

# ---------------- TAB 1: TOP TOPICS ----------------
with tab_top:
    st.markdown("### Most Important Topics (Predicted)")
    top = stats[stats["Score"] > 0].sort_values("Score", ascending=False).head(10)
    top = top.reset_index(drop=True)
    top.index = top.index + 1

    show = top[["Topic", "Unit", "Priority", "Papers", "Times_Asked", "Total_Marks", "Score"]].copy()
    show["Priority"] = show["Priority"].map(lambda p: f"{PRIORITY_ICON[p]} {p}")
    st.dataframe(show)

    st.bar_chart(top.set_index("Topic")["Score"])

    st.markdown("### Not asked yet in these papers")
    st.caption("These syllabus topics did not appear in the analysed papers. Do not ignore them completely.")
    not_asked = stats[stats["Priority"] == "Not asked yet"]
    if len(not_asked) == 0:
        st.write("All syllabus topics have appeared at least once.")
    else:
        for _, row in not_asked.iterrows():
            st.write(f"⚪ {row['Topic']}  —  *{row['Unit']}*")

# ---------------- TAB 2: UNIT-WISE ----------------
with tab_unit:
    st.markdown("### Unit-wise Study Priority")
    unit_score = stats.groupby("Unit")["Score"].sum()
    total_score = unit_score.sum() if unit_score.sum() > 0 else 1

    chart_df = pd.DataFrame(
        {"Score": [unit_score.get(u, 0) for u in UNITS]}, index=list(UNITS.keys())
    )
    st.bar_chart(chart_df)

    for unit in UNITS:
        share = unit_score.get(unit, 0) / total_score
        if share >= 0.30:
            label = "High"
        elif share >= 0.20:
            label = "Medium"
        else:
            label = "Low"
        with st.expander(f"{unit}  —  {PRIORITY_ICON[label]} {label} ({share * 100:.0f}% of total score)"):
            unit_topics = stats[stats["Unit"] == unit].sort_values("Score", ascending=False)
            for _, row in unit_topics.iterrows():
                icon = PRIORITY_ICON[row["Priority"]]
                st.write(
                    f"{icon} **{row['Topic']}**  —  asked {row['Times_Asked']} time(s), "
                    f"{row['Papers']} paper(s), {row['Total_Marks']:g} marks"
                )

# ---------------- TAB 3: SEARCH ----------------
with tab_search:
    st.markdown(f"### Find a Topic in {subject}")
    search = st.text_input("Enter topic name", key="topic_search").strip()

    if search:
        matches = stats[stats["Topic"].str.lower().str.contains(search.lower(), regex=False)]
        if len(matches) > 0:
            st.success(f"{len(matches)} matching topic(s) found:")
            for _, row in matches.iterrows():
                icon = PRIORITY_ICON[row["Priority"]]
                with st.expander(f"📌 {row['Topic']}  —  {icon} {row['Priority']}"):
                    st.write(f"Unit: {row['Unit']}")
                    st.write(
                        f"Asked {row['Times_Asked']} time(s) in {row['Papers']} paper(s), "
                        f"total {row['Total_Marks']:g} marks"
                    )
                    past = df[df["Topic"] == row["Topic"]]
                    if len(past) == 0:
                        st.write("Not asked in the analysed papers.")
                    else:
                        st.write("Past questions:")
                        for _, q in past.iterrows():
                            st.write(f"• ({q['Year']}, {q['Q.No']}, {q['Marks']:g} marks) {q['Question']}")
        else:
            st.warning("No matching topic found.")

# ---------------- TAB 4: PAPER DATA ----------------
with tab_data:
    st.markdown("### Extracted Question Data")
    st.caption("A question that covers more than one topic appears once per topic.")
    st.dataframe(df)
    st.download_button(
        "⬇️ Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="pyq_data.csv",
        mime="text/csv",
    )

# ---------------- TAB 5: ALL SUBJECTS ----------------
with tab_all:
    st.markdown("### All Subjects at a Glance")
    st.dataframe(build_overview())

st.markdown("---")

st.markdown("### Project Progress")
st.write("✅ Python setup completed")
st.write("✅ Required libraries installed")
st.write("✅ Syllabus added for 5 subjects")
st.write("✅ Previous-year papers analysed (Java: 2 papers, others: 1 paper)")
st.write("✅ Rule-based topic scoring and subject selector added")
st.write("⏳ More papers to be added for better accuracy")
st.write("⏳ More subjects pending")

st.caption("ExamPredict AI | BCA Final Year Project")