from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = Path(__file__).resolve().parents[1] / "Response_to_Reviewers_EJIE-337519.docx"


INK = "1F1F1F"
BLUE = "2E5D7B"
DARK_BLUE = "1F4D78"
MUTED = "5E6872"
LIGHT_GRAY = "F2F4F7"
PALE_BLUE = "EDF4F8"
PALE_YELLOW = "FFF7D6"
GREEN = "2D6A4F"
WHITE = "FFFFFF"


def set_cell_or_paragraph_shading(paragraph, fill):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = p_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        p_pr.append(shd)
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")


def set_paragraph_border(paragraph, side="left", color=BLUE, size=12, space=8):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        p_pr.append(p_bdr)
    border = OxmlElement(f"w:{side}")
    border.set(qn("w:val"), "single")
    border.set(qn("w:sz"), str(size))
    border.set(qn("w:space"), str(space))
    border.set(qn("w:color"), color)
    p_bdr.append(border)


def set_keep(paragraph, keep_next=False, keep_lines=True):
    fmt = paragraph.paragraph_format
    fmt.keep_with_next = keep_next
    fmt.keep_together = keep_lines


def set_font(run, name="Calibri", size=11, color=INK, bold=None, italic=None):
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def remove_style_children(style, paragraph_tags=(), run_tags=()):
    """Remove inherited template residue before applying explicit preset tokens."""
    p_pr = style._element.find(qn("w:pPr"))
    if p_pr is not None:
        for tag in paragraph_tags:
            node = p_pr.find(qn(tag))
            if node is not None:
                p_pr.remove(node)
    r_pr = style._element.find(qn("w:rPr"))
    if r_pr is not None:
        for tag in run_tags:
            node = r_pr.find(qn(tag))
            if node is not None:
                r_pr.remove(node)


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)
    set_font(run, size=9, color=MUTED)


def configure_styles(doc):
    styles = doc.styles

    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10
    normal.paragraph_format.widow_control = True

    title_style = styles["Title"]
    title_style.font.name = "Calibri"
    title_style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    title_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    title_style.font.size = Pt(23)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor.from_string(INK)
    title_style.paragraph_format.space_before = Pt(18)
    title_style.paragraph_format.space_after = Pt(4)
    title_style.paragraph_format.line_spacing = 1.0
    title_style.paragraph_format.keep_with_next = True
    remove_style_children(
        title_style,
        paragraph_tags=("w:pBdr", "w:contextualSpacing"),
        run_tags=("w:spacing", "w:kern", "w:szCs"),
    )

    subtitle_style = styles["Subtitle"]
    subtitle_style.font.name = "Calibri"
    subtitle_style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    subtitle_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    subtitle_style.font.size = Pt(13)
    subtitle_style.font.bold = True
    subtitle_style.font.italic = False
    subtitle_style.font.color.rgb = RGBColor.from_string(MUTED)
    subtitle_style.paragraph_format.space_before = Pt(0)
    subtitle_style.paragraph_format.space_after = Pt(16)
    subtitle_style.paragraph_format.line_spacing = 1.0
    subtitle_style.paragraph_format.keep_with_next = True
    remove_style_children(
        subtitle_style,
        paragraph_tags=("w:numPr",),
        run_tags=("w:spacing", "w:iCs", "w:szCs"),
    )

    h1 = styles["Heading 1"]
    h1.font.name = "Calibri"
    h1._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    h1._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor.from_string(BLUE)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(8)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.keep_together = True

    h2 = styles["Heading 2"]
    h2.font.name = "Calibri"
    h2._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    h2._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    h2.font.size = Pt(13)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor.from_string(BLUE)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.keep_with_next = True
    h2.paragraph_format.keep_together = True

    h3 = styles["Heading 3"]
    h3.font.name = "Calibri"
    h3._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    h3._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor.from_string(DARK_BLUE)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.keep_with_next = True
    h3.paragraph_format.keep_together = True

    for name, base in [
        ("Reviewer Comment", "Normal"),
        ("Response Text", "Normal"),
        ("Location", "Normal"),
        ("Internal Note", "Normal"),
    ]:
        if name not in styles:
            styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style = styles[name]
        style.base_style = styles[base]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.size = Pt(10.5 if name == "Reviewer Comment" else 11)
        style.paragraph_format.line_spacing = 1.10
        style.paragraph_format.widow_control = True

    styles["Reviewer Comment"].font.italic = True
    styles["Reviewer Comment"].font.color.rgb = RGBColor.from_string(INK)
    styles["Reviewer Comment"].paragraph_format.left_indent = Inches(0.18)
    styles["Reviewer Comment"].paragraph_format.right_indent = Inches(0.10)
    styles["Reviewer Comment"].paragraph_format.space_before = Pt(2)
    styles["Reviewer Comment"].paragraph_format.space_after = Pt(8)

    styles["Response Text"].paragraph_format.space_after = Pt(6)

    styles["Location"].font.size = Pt(10)
    styles["Location"].font.color.rgb = RGBColor.from_string(GREEN)
    styles["Location"].paragraph_format.space_before = Pt(2)
    styles["Location"].paragraph_format.space_after = Pt(10)

    styles["Internal Note"].font.size = Pt(9.5)
    styles["Internal Note"].font.color.rgb = RGBColor.from_string("6A5700")
    styles["Internal Note"].paragraph_format.left_indent = Inches(0.12)
    styles["Internal Note"].paragraph_format.right_indent = Inches(0.12)
    styles["Internal Note"].paragraph_format.space_before = Pt(4)
    styles["Internal Note"].paragraph_format.space_after = Pt(12)


def add_labeled_paragraph(doc, label, text, after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(label)
    set_font(r, size=10.5, color=MUTED, bold=True)
    r = p.add_run(text)
    set_font(r, size=10.5, color=INK)
    return p


def add_response_item(doc, heading, comment, response_paragraphs, location):
    h = doc.add_paragraph(heading, style="Heading 3")
    set_keep(h, keep_next=True)

    c = doc.add_paragraph(style="Reviewer Comment")
    label = c.add_run("Reviewer comment. ")
    set_font(label, size=10.5, color=DARK_BLUE, bold=True, italic=False)
    body = c.add_run(comment)
    set_font(body, size=10.5, color=INK, italic=True)
    set_cell_or_paragraph_shading(c, LIGHT_GRAY)
    set_paragraph_border(c, side="left", color=BLUE, size=14, space=8)
    set_keep(c, keep_next=True)

    for idx, text in enumerate(response_paragraphs):
        p = doc.add_paragraph(style="Response Text")
        if idx == 0:
            r = p.add_run("Response. ")
            set_font(r, size=11, color=BLUE, bold=True)
        r = p.add_run(text)
        set_font(r, size=11, color=INK)
        # Keep each response paragraph intact where possible, but do not chain
        # all response paragraphs together. Very long keep-with-next chains can
        # force Word to intrude into the top margin on continuation pages.
        set_keep(p, keep_next=False, keep_lines=True)

    p = doc.add_paragraph(style="Location")
    r = p.add_run("Location in revised manuscript. ")
    set_font(r, size=10, color=GREEN, bold=True)
    r = p.add_run(location)
    set_font(r, size=10, color=GREEN)
    set_keep(p, keep_next=False, keep_lines=True)


def build_document():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    configure_styles(doc)

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hp.paragraph_format.space_after = Pt(0)
    r = hp.add_run("EJIE-337519  |  RESPONSE TO REVIEWERS")
    set_font(r, size=8.5, color=MUTED, bold=True)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fp.paragraph_format.space_before = Pt(0)
    fp.paragraph_format.space_after = Pt(0)
    r = fp.add_run("Page ")
    set_font(r, size=9, color=MUTED)
    add_page_field(fp)

    title = doc.add_paragraph(style="Title")
    title.add_run("RESPONSE TO REVIEWERS")

    subtitle = doc.add_paragraph(style="Subtitle")
    subtitle.add_run("Manuscript EJIE-337519")

    add_labeled_paragraph(doc, "Journal: ", "European Journal of Industrial Engineering")
    add_labeled_paragraph(
        doc,
        "Original title: ",
        "Adaptive Heuristics for Order Batching Initiation Timing in Same-Day Delivery Warehouses",
    )
    add_labeled_paragraph(
        doc,
        "Revised title: ",
        "Adaptive Batch-Release and Composition Heuristics for Same-Day Delivery Warehouses: A Discrete-Event Simulation Study",
        after=12,
    )

    note = doc.add_paragraph(style="Internal Note")
    r = note.add_run("AUTHOR FINALISATION NOTE - DELETE BEFORE SUBMISSION. ")
    set_font(r, size=9.5, color="6A5700", bold=True)
    r = note.add_run(
        "Replace every [Page XX, Lines XX-XX] placeholder after journal formatting is final; replace reviewer paraphrases with the exact verbatim wording if required by the submission system; and confirm that every described revision appears in the highlighted manuscript."
    )
    set_font(r, size=9.5, color="6A5700")
    set_cell_or_paragraph_shading(note, PALE_YELLOW)
    set_paragraph_border(note, side="left", color="C49A00", size=14, space=8)

    doc.add_heading("Letter to the Editor and Reviewers", level=1)
    p = doc.add_paragraph()
    r = p.add_run("Dear Editor and Reviewers,")
    set_font(r, size=11, color=INK)

    opening = [
        "We sincerely thank the Editor and both Reviewers for their careful and constructive evaluation of our manuscript. Their comments led us to re-audit the simulation model, rerun the complete experiment, add reviewer-directed experiments, and substantially rewrite the manuscript. We have addressed every comment below in the order in which it was raised. Reviewer comments are shown in italicised shaded text, followed by our response and the location of the corresponding change.",
        "The revised evidence comprises 6,912 factorial scenarios, 30 common-random-number replications per scenario, and 207,360 successful main runs after a 5,460-s Welch warm-up. We also added a 2 x 3 timing-by-composition experiment, separate FTWB/VTWB calibration with tuning and held-out replications, beta sensitivity, and isolated decision-kernel benchmarks. The revised analysis uses paired CRN contrasts and confidence intervals as the primary inferential evidence.",
        "Several conclusions changed materially. MPBH remains the strongest tested policy for deadline performance, but its mean TLO reduction relative to the pooled canonical FTWB/VTWB benchmarks is 10.66%, not 27.04%. The crossed experiment does not support our original proposition that timing has a larger effect than composition; we now report this negative result explicitly. We also corrected the composite-score pipeline, expanded the outcome set, separated release timing from composition, and bounded all theoretical and managerial claims to the simulated domain.",
        "All changes in the accompanying revised manuscript are highlighted for ease of review. Page and line references below are intentionally left as placeholders in this working letter and will be replaced after the journal-formatted revision is paginated.",
    ]
    for text in opening:
        p = doc.add_paragraph(text)
        set_keep(p, keep_lines=True)

    doc.add_heading("Response to Reviewer 1", level=1)
    p = doc.add_paragraph(
        "We are grateful to Reviewer 1 for identifying the principal design confound, benchmark-fairness issue, metric limitations, and opportunities to improve theoretical precision and reproducibility."
    )

    doc.add_heading("Major comments", level=2)

    add_response_item(
        doc,
        "Major Comment 1 - Separation of triggering and batch composition",
        "MPBH combines the decision of when to release work with due-date ordering, temporary-batch construction, feasibility checks, and order removal. The decision layers should be separated explicitly and supported by an ablation study.",
        [
            "We agree. We refactored the conceptual and computational model into four layers: release timing, batch composition, picker assignment, and routing. The revised manuscript identifies which layer is controlled by each policy and no longer treats SNH or MPBH as timing-only methods. The title was also revised to reflect the joint release-and-composition scope.",
            "We conducted a balanced 2 x 3 crossed experiment combining timing (FTWB versus MPBH-immediate timing) with composition (FCFS, EDT, and MPBH), using common random numbers and planned paired contrasts. MPBH timing reduced mean TLO by 18.119 orders relative to FTWB timing (95% CI: 16.090-20.147 fewer). MPBH composition reduced mean TLO by 153.005 orders relative to FCFS (95% CI: 142.186-163.824 fewer) and by 153.041 relative to EDT (95% CI: 142.223-163.859 fewer). EDT and FCFS did not differ reliably (mean difference 0.036; 95% CI: -0.006 to 0.079).",
            "Thus, the tested MPBH-composition effect was approximately 8.4 times the MPBH-timing effect. We now attribute MPBH's performance to coordinated release and composition, report Proposition 4 as not supported, and retain the separate effect estimates and confidence intervals rather than relying on incomparable main effects.",
        ],
        "[Page XX, Lines XX-XX], revised title and Introduction; [Page XX, Lines XX-XX], Sections 3.1 and 3.4; [Page XX, Lines XX-XX], Section 4.4; [Page XX, Lines XX-XX], timing-by-composition results; [Page XX, Lines XX-XX], Discussion.",
    )

    add_response_item(
        doc,
        "Major Comment 2 - Calibration and fairness of FTWB/VTWB benchmarks",
        "The FTWB and VTWB parameter values were transferred from prior work without retuning for the present simulation, potentially making the benchmarks conservative and overstating MPBH's advantage.",
        [
            "We agree that benchmark fairness requires explicit calibration. We evaluated F = {60, 120, 180, 240, 300, 360, 480, 600, 720} s and V = {4, 6, 8, 10, 12, 16, 20, 24} orders. The first 15 replications were used for tuning and the remaining 15 for held-out evaluation, thereby preventing parameter selection on the held-out outcomes.",
            "The tuning split selected F = 60 s and V = 4 for minimum TLO; V = 6 maximised the declared calibration composite. We now report paper-canonical and tuned results separately. During the model re-audit, we also confirmed that the executable paper-canonical FTWB setting is F = 720 s, rather than the 360 s stated in the accepted manuscript; this inconsistency has been corrected transparently. Neither F = 720, V = 12, nor the tuned values are described as universally optimal.",
            "The revised headline comparison uses the pooled canonical FTWB/VTWB benchmark and yields a 10.66% MPBH TLO reduction. Calibration results are presented as robustness and fairness evidence, not as a post-hoc replacement of the main experimental treatments.",
        ],
        "[Page XX, Lines XX-XX], Sections 3.4 and 4.1; [Page XX, Lines XX-XX], benchmark-calibration results and sensitivity figure; [Page XX, Lines XX-XX], Limitations.",
    )

    add_response_item(
        doc,
        "Major Comment 3 - More rigorous mathematical formulation",
        "The mathematical formulation is too high-level. The problem should be formalised more rigorously, for example as an MDP/semi-MDP, or compared with a small offline MIP benchmark.",
        [
            "We strengthened the formulation as an event-driven online decision process. The revised Section 3.1 defines the observable state S_t = (O_t, B_t, P_t, t), a timing action (wait or open a release cycle), a conditional composition action selecting capacity-feasible subsets, stochastic arrival and order-content transitions, picker and tour transitions, and a finite-horizon cost led by TLO. We also define the available release slots so pending batches cannot over-reserve pickers.",
            "We deliberately do not claim to solve the full MDP or obtain a globally optimal policy. The eight methods are specified as transparent heuristic policies, and the crossed experiment distinguishes policy effects from timing- and composition-layer effects. Complete pseudocode and deterministic tie-breaking rules are provided for reproducibility.",
            "We did not add an offline MIP comparison because it would require a different information structure and a separate exact-solution study beyond the present revision. We have stated this explicitly as a limitation and identified exact benchmarks on tractable instances as a priority for future research. We also removed global-optimality language from the research question, results, and conclusion.",
        ],
        "[Page XX, Lines XX-XX], Section 3.1; [Page XX, Lines XX-XX], Sections 4.1-4.4 and Supplementary Algorithm Appendix; [Page XX, Lines XX-XX], Limitations and Future Research.",
    )

    add_response_item(
        doc,
        "Major Comment 4 - Overstatement of Proposition 4",
        "The claim that batch-initiation timing matters more than batch composition is too broad because the original comparison used only FCFS and EDT rather than advanced composition methods.",
        [
            "We agree and have withdrawn the general claim. More importantly, the new crossed experiment yielded the opposite ordering within the tested subset: MPBH timing improved TLO, but MPBH composition produced an effect approximately 8.4 times larger. Proposition 4 is therefore reported as not supported, rather than merely qualified.",
            "The Abstract, Introduction, proposition assessment, Results, Discussion, and Conclusion now state that timing and composition are separable contributors and that coordinated state-aware release and composition is the defensible interpretation. We explicitly limit generalisation to the tested FCFS, EDT, and MPBH composition rules and identify proximity, savings, local-search, VNS, rolling-horizon, and optimisation-based comparators as future work under an equal tuning budget.",
        ],
        "[Page XX, Lines XX-XX], Abstract and Introduction; [Page XX, Lines XX-XX], proposition statements; [Page XX, Lines XX-XX], timing-by-composition results; [Page XX, Lines XX-XX], Discussion and Conclusion.",
    )

    add_response_item(
        doc,
        "Major Comment 5 - Additional performance metrics",
        "TLO is an absolute count that depends strongly on order volume and does not distinguish small from severe lateness. Please add relative service measures and tardiness metrics.",
        [
            "We agree. The rerun persists arrival, due, batch, picker, start, completion, horizon state, censor time, and tardiness fields for each order. The revised manuscript adds late-order ratio, the non-late-at-horizon rate, throughput, completed-order mean tardiness, conditional late tardiness, waiting time, flow time, picker utilisation, cart utilisation, and trip count.",
            "We also corrected the censoring treatment. At the fixed horizon, exact final tardiness is unavailable for unfinished orders. TLO therefore counts completed-late orders plus overdue outstanding orders, while all-order tardiness is reported as a clearly labelled horizon lower bound rather than an imputed completion value. The software field previously called 'on-time rate' is described more precisely as the non-late-at-horizon rate because outstanding orders that are not yet due may be included.",
            "For transparency, MPBH's corrected aggregate values include a mean late ratio of 0.4601, a non-late-at-horizon rate of 53.990%, and completed-order mean tardiness of 1,393.042 s. The corresponding all-order tardiness lower bound is 4,877.198 s, and the difference is discussed as a consequence of right censoring rather than as contradictory evidence.",
        ],
        "[Page XX, Lines XX-XX], Section 3.5 Performance Metrics; [Page XX, Lines XX-XX], expanded main-results table; [Page XX, Lines XX-XX], censoring-aware tardiness results and Limitations.",
    )

    add_response_item(
        doc,
        "Major Comment 6 - Composite-score justification, sensitivity, and inconsistency",
        "The 0.6/0.3/0.1 weights and normalisation scope require justification and sensitivity analysis, and the composite values in the table and narrative are inconsistent.",
        [
            "We agree and performed a full numerical audit. The discrepancy arose because the accepted table normalised within scenario cells whereas the narrative normalised already-aggregated global means. Those values (0.864 and 0.924 for MPBH) are no longer used.",
            "The corrected procedure operates on complete matched scenario-by-replication CRN blocks. Within each block, TLO is reverse min-max normalised, throughput and picker utilisation are benefit-normalised, and a constant range is assigned 0.5. Pareto analysis and unnormalised paired outcomes are primary; the weighted composite is explicitly secondary.",
            "We report the original weights together with equal, throughput-priority, and utilisation-priority schemes. MPBH ranks first under all four schemes and has a corrected original-weight composite of 0.9920. MaxPicker and MPBH are globally Pareto non-dominated. The manuscript now uses one normalisation scope consistently and explains the reason for the accepted-paper discrepancy.",
        ],
        "[Page XX, Lines XX-XX], Section 3.5; [Page XX, Lines XX-XX], corrected main-results table and Pareto/weight-sensitivity analysis; [Page XX, Lines XX-XX], Discussion.",
    )

    add_response_item(
        doc,
        "Major Comment 7 - Reframing the Time-Based Competition contribution",
        "TBC currently functions more as motivation than as a formal theory from which the heuristics are derived. The theoretical contribution should be framed more cautiously.",
        [
            "We agree. The revised manuscript no longer claims to extend TBC theory formally. TBC is used as a temporal-performance lens through which current due-time, workload, and resource information can reduce avoidable waiting at the warehouse decision level.",
            "Consistent with the Reviewer's suggestion, we describe batch release as a micro-operational mechanism for responsiveness, while making clear that the model ends when the picking tour returns to the I/O point. It does not represent packing, vehicle dispatch, customer delivery, cost, market share, or a real-world causal TBC effect. The revised Discussion further notes that temporal competitiveness in this model arises from coordinating when work is released with which orders are released.",
        ],
        "[Page XX, Lines XX-XX], Abstract; [Page XX, Lines XX-XX], Introduction and Section 2.1; [Page XX, Lines XX-XX], Discussion and Managerial Implications.",
    )

    add_response_item(
        doc,
        "Major Comment 10 - More specific and actionable managerial implications",
        "The managerial implications should explain when MPBH is beneficial, when simple rules may suffice, how beta should be calibrated, how picker availability affects policy choice, and how managers should balance TLO, throughput, and utilisation.",
        [
            "We added an evidence-based decision guide organised by operating priority rather than presenting one universal winner. MPBH is the default candidate when deadline performance and throughput dominate; it produced the lowest mean TLO, the highest non-late-at-horizon rate and throughput, and won 770 of 864 operational cells. MaxPicker is the simpler alternative when picker utilisation and implementation simplicity dominate and is the only other globally Pareto non-dominated policy. In a representative low-rate, 12-picker context, FTWB, MPBH, MaxPicker, and SNH all achieved zero mean TLO, so a simpler rule may be sufficient.",
            "We also conducted beta sensitivity. For MPBH, beta = 1 versus beta = 2 reduced TLO by 65.415 orders (95% CI: 60.885-69.946 fewer), but increased mean trips from 174.63 to 212.57 and reduced mean cart utilisation from 52.93% to 37.96%. Higher beta consolidated tours but worsened deadline performance in the tested slice. Thus beta is presented as a service-efficiency control, not a universal optimum.",
            "The guide also advises local F/V calibration and joint consideration of service, trips, labour utilisation, cart fill, and computation. We removed unsupported claims about cost savings and customer satisfaction because no cost model, operational MPID, or empirical warehouse validation was supplied.",
        ],
        "[Page XX, Lines XX-XX], beta-sensitivity results; [Page XX, Lines XX-XX], Section 6.2 and managerial decision guide; [Page XX, Lines XX-XX], Limitations.",
    )

    doc.add_heading("Minor comments", level=2)

    add_response_item(
        doc,
        "Minor Comment 1 - Standardise TLO terminology",
        "The manuscript uses 'total late orders', 'late orders', and 'TLO' inconsistently for the same metric.",
        [
            "We standardised the terminology globally. 'Total late orders (TLO)' is defined at first use, after which 'TLO' is used consistently in the text, equations, tables, and figure captions. We also clarified that TLO includes completed-late orders and overdue outstanding orders at the fixed horizon.",
        ],
        "[Page XX, Lines XX-XX], first definition in Section 3.5; global revisions throughout the manuscript, tables, and figure captions.",
    )

    add_response_item(
        doc,
        "Minor Comment 2 - Accuracy of the SNH name",
        "SNH appears closer to a priority-rule heuristic than to a true neighbourhood search. Please rename it or explain its relationship to neighbourhood search more accurately.",
        [
            "We retained the acronym SNH for continuity but rewrote its definition to remove any implication of iterative neighbourhood search or local optimality. The manuscript now describes SNH as a deterministic structured rule set inspired by alternative neighbourhood priorities, with urgency, capacity, and hybrid fallback orderings. Legacy DVNS labels have been removed, and the exact selection, fallback, capacity, and tie-breaking logic is stated explicitly.",
        ],
        "[Page XX, Lines XX-XX], Section 4.4; corresponding labels in all tables, figures, and supplementary pseudocode.",
    )

    add_response_item(
        doc,
        "Minor Comment 3 - Detailed pseudocode for reproducibility",
        "The one-line decision rules and prose descriptions are insufficient for reproducibility; formal pseudocode should be provided for all heuristics.",
        [
            "We added complete pseudocode for FTWB, VTWB, MaxPicker, MaxCart, UrgentPicker, UrgentCart, SNH, and MPBH in the supplementary algorithm appendix. The algorithms specify event eligibility, release-slot reservation, order sorting, next-fit composition, capacity checks, feasibility restoration, deadlock prevention, termination, picker assignment, and deterministic tie-breaking. Each algorithm is linked to its theoretical bound and the empirical latency benchmark where relevant.",
        ],
        "[Page XX, Lines XX-XX], Sections 4.1-4.4; [Supplementary Page XX, Lines XX-XX], Algorithm Appendix.",
    )

    add_response_item(
        doc,
        "Minor Comment 4 - Warm-up, seeds, and replication design",
        "Please provide more detail on the Welch warm-up procedure, random-seed control, common random numbers, and the replication design.",
        [
            "We expanded the experimental protocol. The Welch study used 24-h runs, ten replications, all eight policies, 60-s observations, an 11-point centred moving average, a 5% tolerance, and ten consecutive stable points in the stable pilot. The maximum stabilisation point was 5,460 s, which is deleted before the eight-hour measurement window. We explicitly distinguish this initialisation deletion from steady-state claims in overloaded cells, where backlog drift remains positive.",
            "The revised manuscript also documents 30 replications per scenario, common random numbers, SHA-256-derived deterministic seeds, UUID5 run identifiers, and fixed tie-breaking. Paired contrasts are computed in complete scenario-by-replication blocks, while uncertainty is based on demand-stream clusters within fixed arrival-rate strata rather than treating all scenario runs as independent replicates.",
        ],
        "[Page XX, Lines XX-XX], Section 3.3; [Page XX, Lines XX-XX], statistical analysis and Limitations.",
    )

    add_response_item(
        doc,
        "Minor Comment 5 - Anticipate UrgentCart's OR-logic interaction",
        "The potential conflict between urgency and cart-capacity branches should be anticipated in the method description rather than explained only after observing poor results.",
        [
            "We revised Section 4.3 to explain the intended role of both OR branches before the results are presented: the urgency branch prevents predicted-at-risk orders from waiting solely for a full cart, while the capacity branch releases a sufficiently loaded pool. We agree that their interaction must be treated as an empirical mechanism, not assumed to be beneficial.",
            "The corrected rerun also changed the substantive finding. Under the canonical main factorial, UrgentCart produced the same matched outcomes as MaxCart for TLO, throughput, picker utilisation, and trip count. We therefore removed the accepted-paper 'worst-of-both-worlds' explanation and now report that the urgency branch was operationally inactive in the tested states, without generalising this equivalence beyond the simulation domain.",
        ],
        "[Page XX, Lines XX-XX], Section 4.3; [Page XX, Lines XX-XX], UrgentCart results and Discussion.",
    )

    add_response_item(
        doc,
        "Minor Comment 6 - Broaden and update the literature review",
        "The literature review should cover recent dynamic/online batching, real-time dispatching rules, and integrated order-fulfilment systems more comprehensively.",
        [
            "We expanded the literature review around these three themes and revised the research-gap statement. The revised review distinguishes learning-based and rolling-horizon methods from transparent dispatch rules, recognises that release, assignment, sequencing, and routing may be interdependent, and positions our contribution as reproducible evidence on state-aware release and the separate contribution of timing and composition rather than as an absence of dynamic batching research.",
            "The bibliography has been updated with recent, publisher-verified work from 2023-2026, including relevant EJIE contributions, and every new reference is discussed in the text rather than added only to the reference list. The final reference details will be checked once more against publisher records before submission.",
        ],
        "[Page XX, Lines XX-XX], Sections 2.2-2.4; [Page XX, Lines XX-XX], updated References.",
    )

    doc.add_heading("Response to Reviewer 2", level=1)
    p = doc.add_paragraph(
        "We thank Reviewer 2 for emphasising current scholarship, notational clarity, empirical scalability, and practical decision support. These comments materially improved the manuscript's accessibility and implementation relevance."
    )

    add_response_item(
        doc,
        "Major Comment 1 - Update the literature review",
        "The reference base is relatively old and the literature review should be updated with more recent work.",
        [
            "We agree. As also noted in our response to Reviewer 1, Minor Comment 6, we expanded Sections 2.2-2.4 to incorporate recent work on dynamic and online batching, real-time dispatching, integrated fulfilment, reoptimisation, and transparent versus learning-based policy classes. We also revised the gap statement so it does not overstate novelty relative to this newer literature.",
            "The revised reference list includes relevant recent EJIE and broader industrial-engineering studies from 2023-2026. Only references verified against publisher metadata are retained, and each addition is integrated into the argument of the literature review.",
        ],
        "[Page XX, Lines XX-XX], Sections 2.2-2.4; [Page XX, Lines XX-XX], updated References. See also Response to Reviewer 1, Minor Comment 6.",
    )

    add_response_item(
        doc,
        "Major Comment 2 - Reorganise Table 3 and clarify notation",
        "Table 3 should separate variables from parameters and clarify ambiguous definitions, particularly ProcessingTime(o) and TotalBatchTime.",
        [
            "We replaced the original notation table with two blocks: dynamic variables/outcomes and fixed/experimental parameters, each with an explicit unit or type. The revised definitions distinguish arrival, due, start, and completion times; order lines and pieces; the measurement cohort; available release slots; TLO; throughput; utilisation; and the composite score.",
            "We removed the ambiguous generic ProcessingTime(o) and TotalBatchTime definitions. Executed tour time is now stated explicitly as 180 s setup plus exact route walking time plus 5 s per piece, with setup charged once per tour. The urgency test is separately defined as a single-order completion-risk estimate using a calibrated travel surrogate. We report the surrogate features, frozen calibration, held-out error, caching, and the fact that exact routing - not the surrogate - determines executed tour time.",
        ],
        "[Page XX, Lines XX-XX], revised Tables 3a and 3b; [Page XX, Lines XX-XX], Section 3.2.",
    )

    add_response_item(
        doc,
        "Major Comment 3 - Actual computation time and scalability",
        "Because the setting is dynamic, practical implementation requires actual computation-time results and a discussion of scalability, not only theoretical Big-O statements.",
        [
            "We agree and added an isolated decision-kernel benchmark with pool sizes n = {10, 50, 100, 500, 1,000, 5,000}, 30 timing repetitions per cell, and measured timer-overhead subtraction. The protocol and hardware are reported: Intel i7-7700 (4 cores/8 threads), 31.88 GiB RAM, Windows 11, and Python 3.14.6.",
            "At n = 5,000, median adjusted decision latency was approximately 61.34 ms for MPBH, 14.07 ms for SNH, 6.11 ms for UrgentCart, 5.16 ms for UrgentPicker, and 0.38 ms for MaxCart; FTWB, VTWB, and MaxPicker were effectively below 0.01 ms after overhead adjustment. The empirical classifications were practically constant for FTWB, VTWB, and MaxPicker; O(n) for MaxCart, MPBH, SNH, and UrgentPicker; and O(n log n) for UrgentCart in the tested implementation and range.",
            "We now distinguish empirical fits from algorithmic upper bounds and qualify the implementation claim. The results support algorithmic feasibility at the tested scale, but they exclude database, network, WMS integration, and concurrency latency and therefore do not establish end-to-end production response time.",
        ],
        "[Page XX, Lines XX-XX], reviewer-directed experimental protocol; [Page XX, Lines XX-XX], computational performance and scaling results; [Page XX, Lines XX-XX], Managerial Implications and Limitations.",
    )

    add_response_item(
        doc,
        "Major Comment 4 - Practical guidance for heuristic selection",
        "To strengthen the contribution, provide practical guidance for selecting an appropriate heuristic under different operational scenarios.",
        [
            "We agree and added a dedicated managerial decision guide, cross-referenced to the corrected factorial results, Pareto analysis, calibration, beta sensitivity, and latency benchmark. The guide distinguishes deadline/throughput priority (MPBH), simpler high-utilisation operation (MaxPicker), low-rate abundant-picker settings where several rules tie at zero TLO, more aggressive service via beta = 1, greater tour consolidation via higher beta, and local calibration of static F/V parameters.",
            "The guidance is deliberately conditional. MPBH is the strongest tested aggregate policy, not a universal optimum; MaxPicker remains Pareto non-dominated; and policy choice must consider service, trip count, cart fill, labour utilisation, computation, and local integration constraints together. This response is integrated with Reviewer 1, Major Comment 10 to avoid duplicating two separate frameworks.",
        ],
        "[Page XX, Lines XX-XX], Section 6.2 and managerial decision guide. See also Response to Reviewer 1, Major Comment 10.",
    )

    doc.add_heading("Closing statement", level=1)
    closing = [
        "We again thank the Editor and both Reviewers for comments that substantially improved the validity, transparency, and scope discipline of the study. The revised manuscript now reports the corrected full-factorial evidence, the negative timing-versus-composition result, calibrated benchmark comparisons, additional censoring-aware outcomes, composite sensitivity, computational scaling, and conditional managerial guidance.",
        "We have also updated the problem formulation, notation, algorithms, reproducibility protocol, literature review, limitations, data-availability language, and conclusion. All revisions are highlighted in the accompanying manuscript, and the final response letter will include completed page and line references after journal formatting.",
    ]
    for text in closing:
        doc.add_paragraph(text)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Sincerely,")
    set_font(r, size=11, color=INK)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("The Authors")
    set_font(r, size=11, color=INK, bold=True)

    # Metadata and compatibility settings.
    props = doc.core_properties
    props.title = "Response to Reviewers - EJIE-337519"
    props.subject = "Major revision response letter"
    props.author = "The Authors"
    props.keywords = "EJIE-337519; response to reviewers; major revision"
    props.comments = "Working response letter with page and line placeholders requested by the authors."

    settings = doc.settings.element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")

    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    output = build_document()
    print(output)
