// Generates navodila-pred-tecajem.docx (instructor pre-course instructions, Slovenian)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber,
} = require("docx");

const B = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: B, bottom: B, left: B, right: B };

const p = (text, opts = {}) => new Paragraph({ spacing: { after: 120 }, ...opts, children: [new TextRun({ text, ...(opts.run || {}) })] });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const bullet = (children) => new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 80 }, children });
const bl = (text) => bullet([new TextRun(text)]);
const blb = (boldPart, rest) => bullet([new TextRun({ text: boldPart, bold: true }), new TextRun(rest)]);
const num = (ref) => (text) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80 }, children: [new TextRun(text)] });
const mono = (text) => new Paragraph({
  spacing: { after: 120 }, indent: { left: 360 },
  shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
  children: [new TextRun({ text, font: "Consolas", size: 18 })],
});

const cell = (txt, { w, bold = false, fill, head = false } = {}) => new TableCell({
  borders, width: { size: w, type: WidthType.DXA },
  ...(fill ? { shading: { fill, type: ShadingType.CLEAR } } : {}),
  verticalAlign: VerticalAlign.CENTER,
  children: [new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: txt, bold: bold || head, size: head ? 20 : 20 })] })],
});

const warnBox = (title, lines) => new Table({
  columnWidths: [9360],
  margins: { top: 120, bottom: 120, left: 180, right: 180 },
  rows: [new TableRow({
    children: [new TableCell({
      borders, width: { size: 9360, type: WidthType.DXA },
      shading: { fill: "FDEBD0", type: ShadingType.CLEAR },
      children: [
        new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: title, bold: true })] }),
        ...lines.map((l) => new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: l, size: 20 })] })),
      ],
    })],
  })],
});

const timeline = [
  ["čet 11. – pet 12. 6.", "Korak 1 in 2: objava podatkov + DATA_BASE_URL; sporočilo Alešu"],
  ["do ned 14. 6.", "Korak 4: obvestilo študentom (Google račun 18+, prenosnik)"],
  ["do tor 16. 6. zvečer", "Korak 3: pilot A01 + A02 v Colabu; povezave pripravljene za deljenje"],
  ["sre 17. 6.", "DELAVNICA A01 Pandas (9.00–13.00) · A02 First ML Models (15.00–19.00)"],
  ["do čet 18. 6.", "Pilot A03 + obeh domačih nalog v Colabu"],
  ["pet 19. 6.", "DELAVNICA A03 (9.00–12.00) · briefing OBEH domačih nalog — objavite kanal oddaje in utež HW1 : HW2"],
  ["≈ ned 21. 6.", "Suhi preizkus »hallucination hunt« za A04 (vedenje Geminija se spreminja)"],
  ["pon 22. 6.", "DELAVNICA A04 LLMs for Business Decisions (9.00–12.00)"],
  ["pon 29. 6.", "(Aleš) Vibe coding 1 — dogovorjeno orodje velja tudi za A05"],
  ["tor 30. 6.", "ROK HW1 (23.59) · help session za obe nalogi 13.00–17.00"],
  ["sre 1. 7.", "DELAVNICA A05 Vibe Coding (9.00–12.00) · ROK HW2 (23.59)"],
  ["pet 3. 7.", "Predstavitve projektov MADA"],
];

const files = [
  ["planning/tasks.md", "vse odprte naloge s prioritetami (P1–P3)"],
  ["workshops/README.md", "tehnična navodila: objava podatkov, rebuild, predtečajna checklista"],
  ["workshops/lab-aNN-…/instructor-notes.md", "minutni plan, kontrolne številke in pasti za vsako delavnico — odprite pred vsako sejo"],
  ["workshops/lab-a03-…/homework2/GRADING.md", "ocenjevalna rubrika HW2 (70 % objektivno / 30 % subjektivno) + lestvica točk → ocena"],
  ["workshops/_build/verify_course.py", "celovita verifikacija projekta — po vsaki spremembi mora javiti vse zeleno"],
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { size: 44, bold: true, font: "Arial" }, paragraph: { spacing: { before: 120, after: 80 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: "Arial", color: "1F3864" }, paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: "Arial", color: "2E5395" }, paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
      { reference: "pregled", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
      { reference: "korak1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "IMB 2026 · MADA · navodila za izvajalca", size: 16, color: "888888" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Stran ", size: 16 }), new TextRun({ children: [PageNumber.CURRENT], size: 16 }), new TextRun({ text: " / ", size: 16 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16 })] })] }) },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Navodila pred začetkom tečaja")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "IMB 2026 · MADA — podatkovno-AI sklop (delavnice A01–A05) · stanje: 11. junij 2026 · tečaj: 15. 6. – 3. 7. 2026", size: 20, color: "666666" })] }),

      p("Vsa gradiva so zgrajena in preverjena: pet delavniških Colab zvezkov, dve domači nalogi z ocenjevalno rubriko, podatki, inštruktorski zapiski; avtomatska verifikacija javlja 106/106 uspešnih preverjanj. Pred začetkom tečaja je treba opraviti še pet korakov, ki jih lahko opravite samo vi."),

      h1("Pregled — pet korakov"),
      num("pregled")("Objavite podatkovne mape in nastavite DATA_BASE_URL (P1, danes–jutri)."),
      num("pregled")("Uskladite se z Alešem glede AI-orodja za vibe coding (P1, danes)."),
      num("pregled")("Pilotno preverite zvezke v pravem Colabu (P2; A01 in A02 najpozneje 16. 6.)."),
      num("pregled")("Obvestite študente: Google račun (18+) in prenosnik (do 14. 6.)."),
      num("pregled")("Določite utež HW1 : HW2 v skupni oceni (pred 19. 6.)."),

      h1("Korak 1 · Objava podatkov in DATA_BASE_URL (P1)"),
      p("Zvezki nalagajo podatke prek konstante DATA_BASE_URL v prvi kodni celici. Brez nje deluje zasilna pot (študent ročno naloži datoteke), kar je za polno učilnico nerodno. Najčistejša rešitev je javen GitHub repozitorij, ki vsebuje SAMO podatkovne mape."),
      warnBox("⚠ Česa NE objavite javno", [
        "workshops/_build/ — vsebuje referenčne rešitve domačih nalog (smoke testi) in ground_truth.json;",
        "instructor-notes.md (vse delavnice) — vsebujejo kontrolne številke in opise pasti za ocenjevanje.",
        "GRADING.md je lahko javen (rubriko študenti tako ali tako vidijo).",
      ]),
      h2("Postopek"),
      num("korak1")("Ustvarite nov JAVEN repozitorij (npr. imb2026-mada-data) na GitHubu."),
      num("korak1")("Vanj prekopirajte samo mape data/ (in homework/data/, homework2/data/) — ohranite strukturo workshops/lab-a01-…/data itd."),
      num("korak1")("URL surove (raw) mape sporočite asistentu Claude (»vbaka« ga v vse zvezke prek builderjev in vse regenerira) — ali pa URL pred deljenjem ročno vpišete v prvo celico vsakega zvezka v Colabu."),
      mono("primer: DATA_BASE_URL = \"https://raw.githubusercontent.com/<uporabnik>/imb2026-mada-data/main/lab-a01-pandas-business-data/data\""),

      h1("Korak 2 · Uskladitev z Alešem (P1)"),
      bl("Katero AI-orodje bo uporabil pri Vibe coding 1 (29. 6.)? Isto orodje prevzame vaša delavnica A05 (1. 7.)."),
      blb("Pogoj: ", "orodje mora biti za študente brezplačno in NE sme biti Gemini CLI — brezplačni dostop zanj uradno ugasne 18. 6. 2026, sredi tečaja. Varna privzeta izbira: Colabov vgrajeni Gemini (chat panel / Data Science Agent)."),
      bl("Uskladite tudi sporočilo študentom: osebni Google račun je pogoj za Colab AI in Gemini."),

      h1("Korak 3 · Pilot v pravem Colabu (P2)"),
      p("Lokalno je preverjeno vse, česar se da (vsa koda rešitev teče na pravih podatkih). Štirih stvari pa ni mogoče preveriti zunaj Colaba — preverite jih vi, najprej za A01 in A02 (do 16. 6. zvečer):"),
      bl("Runtime → Run all se izvede brez napak na BREZPLAČNEM računu;"),
      bl("zložene rešitve (»Show solution«) se pravilno odpirajo, grafi se izrišejo;"),
      bl("Learn Mode je viden (ikona iskrice) — to je priporočeni vir namigov za študente;"),
      bl("v A04: celica google.colab.ai deluje; na SVEŽEM računu preizkusite tri vprašanja »hallucination hunt« (pričakovani scenariji so v instructor-notes A04)."),
      p("Roki pilotov: A03 + obe domači nalogi do 18. 6., A04 okoli 21. 6., A05 do 30. 6."),

      h1("Korak 4 · Obvestilo študentom (do 14. 6.)"),
      bl("Potrebujejo osebni Google račun (18+) in prenosnik."),
      bl("Povejte, kako bodo prejeli povezave do zvezkov (Drive/Colab ali GitHub)."),
      bl("Odločite se, kam oddajo domači nalogi (oddaja = Colab povezava za ogled): e-pošta ali LMS — in to objavite ob briefingu 19. 6."),

      h1("Korak 5 · Utež HW1 : HW2 (pred 19. 6.)"),
      p("HW1 (regresija, rok 30. 6.) in HW2 (klasifikacija »win-back«, rok 1. 7.) imata vsaka svojo rubriko; HW2 se interno ocenjuje 70 % objektivno / 30 % subjektivno (zasidrani opisniki v GRADING.md). Določiti morate samo še medsebojno utež obeh nalog v skupni oceni predmeta (npr. 40 : 60, ker je HW2 obsežnejša) in jo objaviti ob briefingu."),

      h1("Rutina in pravila med tečajem"),
      blb("Pred vsako delavnico: ", "odprite instructor-notes.md tiste delavnice — minutni plan, točne kontrolne številke (umerjeni podatki: vsi študenti dobijo enake rezultate) in pasti dneva."),
      blb("Nikoli ročno ne urejajte ", "zvezkov (.ipynb) ali CSV-jev — so generirani. Spremembe gredo prek workshops/_build (generate_data.py, build_aNN.py), nato poženite smoke teste in verify_course.py (vse mora biti zeleno)."),
      blb("Ocenjevanje: ", "za obe nalogi so v instructor-notes A03 pričakovani rezultati in samodejne zastavice (npr. točnost ≥ 0,95 pri HW2 pomeni uporabo prepovedanega stolpca voucher_redeemed = puščanje podatkov)."),

      h1("Časovnica"),
      new Table({
        columnWidths: [2340, 7020],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [cell("Datum", { w: 2340, head: true, fill: "D5E8F0" }), cell("Naloga / dogodek", { w: 7020, head: true, fill: "D5E8F0" })] }),
          ...timeline.map(([d, t]) => new TableRow({ children: [cell(d, { w: 2340, bold: true }), cell(t, { w: 7020 })] })),
        ],
      }),

      h1("Ključne datoteke"),
      new Table({
        columnWidths: [3900, 5460],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [cell("Pot", { w: 3900, head: true, fill: "D5E8F0" }), cell("Vsebina", { w: 5460, head: true, fill: "D5E8F0" })] }),
          ...files.map(([f, d]) => new TableRow({ children: [cell(f, { w: 3900 }), cell(d, { w: 5460 })] })),
        ],
      }),
    ],
  }],
});

const out = path.resolve(__dirname, "..", "..", "navodila-pred-tecajem.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes"); });
