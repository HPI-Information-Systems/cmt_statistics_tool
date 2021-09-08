from tqdm import tqdm

from vldb.helper import fillna_strs, get_or_add, read_original_revision
from vldb.tables import RevisionReview, SubmissionReview, async_session


async def insert_reviews(file: str) -> None:
    original, revision = read_original_revision(file)
    original = fillna_strs(
        original,
        [
            "Q6 (Three (or more) strong points about the paper. Please be precise and explicit; clearly explain the value and nature of the contribution.)",
            "Q7 (Three (or more) weak points about the paper. Please clearly indicate whether the paper has any mistakes, missing related work, or results that cannot be considered a contribution; write it so that the authors can understand what is seen as negative.)",
            "Q13 (Detailed Evaluation (Contribution, Pros/Cons, Errors); please number each point and please provide as constructive feedback as possible.)",
            "Q14 (Supplemental material. If the authors have provided supplemental material (data, code, etc.,), is the information likely to be sufficient to understand and to reproduce the experiments? Note that we do not expect actual reproducibility experiments, but rather a verification that the files are in fact there and are reasonable in scope and content.)",
            "Q15 (Revision. If revision is required, list specific required revisions you seek from the authors. Please number each point.)",
            "Q17 (Confidential comments for the PC Chairs. Please add any information that may help us reach a decision.)",
            "Q18 (Name and affiliation of external expert (!) reviewer (if applicable).)",
        ],
    )
    revision = fillna_strs(
        revision,
        [
            "Q6 (Additional comments to the authors on the revised version of the paper)",
            "Q18 (Confidential Comments for the PC Chairs. Please add any information that may help us reach a decision.)",
        ],
    )
    async with async_session() as session:
        for _, row in tqdm(
            original.iterrows(), desc="Reviews Submissions", total=len(original)
        ):
            async with session.begin():
                submission = SubmissionReview(
                    reviewer=(
                        await get_or_add(
                            session,
                            row["Reviewer Name"].strip(),
                            row["Reviewer Email"].strip(),
                            "",
                        )
                    ),
                    submission_id=row["Paper ID"],
                    overall_rating=row["Q1 (Overall Rating)"],
                    relevance=row["Q2 (Relevant for PVLDB)"],
                    revision_possible=row[
                        "Q3 (Are there specific revisions that could raise your overall rating?)"
                    ],
                    paper_flavor=row[
                        "Q4 (Flavor of Regular Research Paper. Please indicate which flavor or flavors best describe the paper.)"
                    ],
                    summary=row[
                        "Q5 (Summary of the paper (what is being proposed and in what context) and a brief justification of your overall recommendation. One solid paragraph.)"
                    ],
                    strengths=row[
                        "Q6 (Three (or more) strong points about the paper. Please be precise and explicit; clearly explain the value and nature of the contribution.)"
                    ],
                    weaknesses=row[
                        "Q7 (Three (or more) weak points about the paper. Please clearly indicate whether the paper has any mistakes, missing related work, or results that cannot be considered a contribution; write it so that the authors can understand what is seen as negative.)"
                    ],
                    novelty=row[
                        "Q8 (Novelty. Please give a high novelty ranking to papers on new topics, opening new fields, or proposing truly new ideas; assign medium ratings to delta papers and papers on well-known topics but still with some valuable contribution.)"
                    ],
                    significance=row["Q9 (Significance)"],
                    technical_depth=row["Q10 (Technical Depth and Quality of Content)"],
                    experiments=row["Q11 (Experiments)"],
                    presentation=row["Q12 (Presentation)"],
                    details=row[
                        "Q13 (Detailed Evaluation (Contribution, Pros/Cons, Errors); please number each point and please provide as constructive feedback as possible.)"
                    ],
                    reproducibility=row[
                        "Q14 (Supplemental material. If the authors have provided supplemental material (data, code, etc.,), is the information likely to be sufficient to understand and to reproduce the experiments? Note that we do not expect actual reproducibility experiments, but rather a verification that the files are in fact there and are reasonable in scope and content.)"
                    ],
                    revision_items=row[
                        "Q15 (Revision. If revision is required, list specific required revisions you seek from the authors. Please number each point.)"
                    ],
                    confidence=row["Q16 (Rate your confidence in this review.)"],
                    confidential_comments=row[
                        "Q17 (Confidential comments for the PC Chairs. Please add any information that may help us reach a decision.)"
                    ],
                    external_reviewer=row[
                        "Q18 (Name and affiliation of external expert (!) reviewer (if applicable).)"
                    ],
                    trainee_agreement=row[
                        "Q19 (I understand that I am allowed to discuss a paper submission with a trainee for the purpose of teaching them how to review papers. I understand that (a) I am responsible to ensure that there is no COI according to the rules published at PVLDB.org between the trainee and any of the authors of the paper. (b) I have informed the trainee about the confidentiality of the content of the paper. (c) I am solely responsible for the final review. [If the trainee contributed significantly to the paper review, please list them above as external reviewer].)"
                    ],
                )
                session.add(submission)
        for _, row in tqdm(
            revision.iterrows(), desc="Reviews Revisions", total=len(revision)
        ):
            async with session.begin():
                revision = RevisionReview(
                    reviewer=(
                        await get_or_add(
                            session,
                            row["Reviewer Name"].strip(),
                            row["Reviewer Email"].strip(),
                            "",
                        )
                    ),
                    revision_id=row["Paper ID"],
                    recommendation=row["Q1 (Final and Overall Recommendation)"],
                    revision_addressed=row[
                        "Q3 (Did the authors satisfactorily address the revision requirements identified in the meta-review of the original submission?)"
                    ],
                    justification=row[
                        "Q5 (Justify your answer to the above question by briefly addressing key revision items.)"
                    ],
                    comments_authors=row[
                        "Q6 (Additional comments to the authors on the revised version of the paper)"
                    ],
                    confidential_comments=row[
                        "Q18 (Confidential Comments for the PC Chairs. Please add any information that may help us reach a decision.)"
                    ],
                )
                session.add(revision)
