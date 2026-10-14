# راهنمای تکمیل مقاله برای Codex

**مقالهٔ مبنا:** *Temporal Retiming Attacks on Hybrid Quantum Spiking Classifiers*، نسخهٔ هشت‌صفحه‌ای `main.pdf` ارسال‌شده در این گفتگو.

**تاریخ بررسی منابع:** 2026-10-14. این فایل برنامهٔ اعمال تغییرات است؛ خود مقاله هنوز با این پیشنهادها ویرایش نشده است.

## 1. دستور اجرایی برای Codex

این فایل را کامل بخوان و تغییرات الزامی بخش‌های 2 تا 9 را روی سورس LaTeX همین مقاله اعمال کن. ابتدا ساختار پروژه، دستورهای محلی و فایل‌های bibliography را بررسی کن. مسیرهای زیر مربوط به ساختار شناخته‌شدهٔ پروژه‌اند؛ اگر ساختار متفاوت است، فایل متناظر را با عنوان بخش و عبارت‌های لنگر پیدا کن. متن انگلیسی بلوک‌ها آمادهٔ درج است، ولی نمادگذاری و ارجاع‌های داخلی را با نسخهٔ واقعی سازگار کن. با وجود تغییرات محلی کاربر، تغییرهای نامرتبط را بازنویسی نکن.

هدف: پیشینهٔ دقیق‌تر، جایگاه روشن‌تر کار، تحلیل علمی عمیق‌تر و تفسیر قوی‌تر نتایج موجود. افزودن منبع به‌تنهایی نتیجهٔ تجربی تازه ایجاد نمی‌کند. آزمایش جدید، عدد حدسی، نمودار مصنوعی یا ادعای quantum advantage اضافه نکن. دستورهای بخش «آزمایش‌های آینده» صرفاً به‌صورت future work در مقاله بیایند؛ برای اجرای این درخواست نیاز به اجرای آموزش یا حملات نیست.

خروجی مورد انتظار: سورس ویرایش‌شده، PDF کامپایل‌شده در صورت وجود ابزار، و گزارشی کوتاه از فایل‌های تغییرکرده، منابع افزوده‌شده و محدودیت‌های حل‌نشده. Git push و بارگذاری Overleaf بخشی از این دستور نیست.

## 2. حدود شواهد: این موارد باید حفظ شوند

- مدل نهایی QSNN-v3 دارای هشت کیوبیت، frontend کلاسیک Conv/LIF، 40,762 پارامتر و readout خطی از تمام 256 احتمال اندازه‌گیری است. شبیه‌سازی statevector تحلیلی است؛ آزمایش سخت‌افزار یا finite-shot برای این مدل گزارش نشده است.
- دقت پنج seed برابر `97.272% ± 0.212%` روی validation است. seedها frontend ازپیش‌آموزش‌دیده و split مشترک دارند؛ این مقدار را به official-test accuracy تبدیل نکن.
- حملات timestamp روی همان 100 نمونهٔ مشترک clean-correct از validation و seed 42 اجرا شده‌اند. PGD در هر دو بودجه 3 موفقیت دارد؛ TEMP با 21 candidate یا 41 forward به‌ترتیب 4 و 3 موفقیت، و با تطبیق زمان 4 و 5 موفقیت دارد. p-valueهای زوجی QSNN به‌ترتیب 1، 1 و 0.5 هستند؛ برتری معنادار TEMP اثبات نشده است.
- `TEMP-DRIFT-v2` نهایی objective مبتنی بر class margin دارد. نام آن مجوز ادعای بهینه‌سازی quantum fidelity یا state drift نیست.
- مطالعهٔ packet-grid کلاسیک، مطالعه‌ای جدا با 1,000 نمونهٔ مشترک clean-correct از test برای هر representation است. نمونه‌ها و واحد بودجه با مطالعهٔ timestamp یکی نیستند. binary و integer نیز manifest مشترک با یکدیگر ندارند.
- clean accuracy در جدول grid روی کل 10,000 نمونهٔ test محاسبه شده است؛ مخرج ASR برابر 1,000 است. دو نوع درصد را با یکدیگر ترکیب نکن.
- هیچ عددی از مقالات دیگر وارد جدول نتایج خودمان نشود. کم بودن ASR حملهٔ محدود، robustness certificate نیست. اختلاف بین مطالعات اثبات علت بودن representation یا quantum component نیست.
- شواهد این نسخه عمدتاً گزارش‌های حفظ‌شده‌اند؛ بازتولید کامل آزمایش‌ها انجام نشده و بسیاری از raw artifacts غایب‌اند. این محدودیت حذف نشود.

## 3. اصلاح Introduction و برجسته‌کردن سهم واقعی

**فایل محتمل:** `sections/introduction.tex`.

عبارت مرکزی فعلی `the observed retiming vulnerability depends on both the representation and the computational comparison` از نظر علی بیش از شواهد موجود قابل برداشت است. آن را با جملهٔ دقیق زیر جایگزین کن؛ باقی عددهای همان پاراگراف حفظ شوند:

```latex
Its central finding is that \textbf{retiming outcomes must be interpreted within their specified input representation and computational budget}. Within the timestamp experiment, the numerical comparison changes with the definition of matched computation; across the separate timestamp and packet-grid studies, differences in victims, populations and budget units preclude a causal representation ablation or a pooled robustness ranking.
```

پیش از فهرست contributions این پاراگراف را اضافه کن:

```latex
The contribution is therefore an evaluation of an implemented hybrid pipeline under explicit temporal constraints, rather than a claim that quantum processing is intrinsically vulnerable or robust. Recent quantum-classifier studies examine how encodings, model structure and adversarial access affect robustness \cite{wendlinger2024comparative,gong2024randomized,dowling2026guarantees}. Our setting adds the event-to-feature transformation: the adversary changes event timing before a classical spiking frontend and a quantum probability readout. This distinction makes end-to-end feasibility and computational accounting necessary parts of the experimental claim.
```

سه contribution فعلی حفظ و مختصر شوند. تحلیل بخش 6 را می‌توان در contribution اول به‌صورت «a margin-based interpretation of the probability readout» ذکر کرد؛ آن را theorem جدید بنیادی یا روش دفاعی معرفی نکن. از عبارت‌های «first-ever»، «state-of-the-art attack»، «quantum supremacy» و «statistically superior» استفاده نشود.

## 4. گسترش Related Work با متن آماده

**فایل محتمل:** `sections/related_work.tex`. دو پاراگراف کوتاه فعلی را با متن زیر جایگزین کن. کلیدهای bibliography موجود از جمله `yu2026`، `brand2024` و `spate2026` را دوباره نساز.

```latex
\paragraph{Raw-event attacks and constrained retiming.}
Surrogate-gradient learning provides a practical route through the nondifferentiable dynamics of spiking networks \cite{neftci2019}. However, an attack on an aggregated tensor and an attack on the underlying event stream need not have the same feasible set. Yao et al. attack raw event data using a probabilistic treatment of discrete event values and sparsity control \cite{yao2024rawevent}. Their construction permits event-value and support changes, whereas our native-event threat model preserves event identities, coordinates, polarities and count. Du et al. investigate raw-event attacks with configurable latencies \cite{du2026latencies}, providing a particularly relevant connection to temporal manipulation. These works motivate attacks at the event interface without making their constraints interchangeable with ours.

\paragraph{Capacity constraints and representation-specific budgets.}
Yu et al. formalize capacity-one spike retiming and budgets on maximum displacement, total delay and the number of retimed spikes \cite{yu2026}. Our classical packet-grid comparison uses a local implementation of this framework, with completed results for maximum displacement and retimed-packet count. The native-timestamp experiment instead permits multiple events to contribute to a frame cell. Its duration-scaled timestamp radius cannot be identified with a one-bin packet displacement. We consequently compare attacks within each stated regime and do not rank the regimes by their raw ASR values.

\paragraph{Hybrid spiking and quantum models.}
Quantum temporal models encompass distinct computational constructions. Brand and Petruccione develop a quantum leaky integrate-and-fire neuron and network \cite{brand2024}; Jha et al. combine SNN-derived EEG features with quantum-kernel classification \cite{jha2025hybrid}; and SPATE studies spike-derived temporal quantum encodings \cite{spate2026}. QSNN-v3 instead composes classical Conv/LIF dynamics, a learned angle map, a data-re-uploading variational circuit \cite{perez2020}, and a linear classifier on the complete measurement-probability vector. These differences concern the model and interface, so accuracy or security claims do not transfer directly between the constructions.

\paragraph{Adversarial robustness of quantum classifiers.}
Wendlinger et al. compare quantum and classical classifiers using transfer attacks, perturbation structure and Lipschitz-based analysis \cite{wendlinger2024comparative}. Gong et al. investigate randomized encodings under specified adversarial-access assumptions \cite{gong2024randomized}, while Dowling et al. establish robustness guarantees for particular quantum-classifier settings \cite{dowling2026guarantees}. Together, these studies motivate stating the encoding and adversary explicitly. Their guarantees and defenses cannot be assigned to QSNN-v3 without checking the corresponding assumptions, especially because our perturbation enters before a classical event-processing frontend.

\paragraph{Evaluation strength and computational controls.}
PGD is a standard iterative baseline \cite{madry2018}, but the failure of one optimizer is insufficient evidence of robustness \cite{carlini2019,athalye2018obfuscated}. Diverse attacks and improved optimization can expose failures missed by an individual configuration \cite{croce2020reliable}. We therefore report paired outcomes under candidate, forward-pass and elapsed-time controls. These controls answer different resource questions and do not establish optimality of either attack. Standard image-space attack ensembles also require adaptation before they respect our order, timing and packet constraints.
```

## 5. اضافه‌کردن یک جدول مقایسهٔ مفهومی

**محل:** انتهای Related Work. این جدول benchmark یا ارزیابی دوبارهٔ مقالات نیست. عنوان و caption باید این موضوع را روشن کنند. اگر محدودیت صفحه وجود دارد، جدول به supplement منتقل و در متن ارجاع داده شود. هیچ ردیف ASR خارجی اضافه نکن.

```latex
\begin{table*}[t]
\centering
\small
\caption{Conceptual positioning of related work. Entries describe research scope, not a common benchmark or an experimental ranking.}
\label{tab:literature_scope}
\begin{tabular}{p{0.20\textwidth}p{0.32\textwidth}p{0.39\textwidth}}
\hline
Work & Studied interface or construction & Relation to the present study \\
\hline
Yao et al.\ \cite{yao2024rawevent} & Raw-event attacks with discrete-value optimization and sparsity control & Motivates the raw-event interface; not restricted to our identity-preserving retiming. \\
Du et al.\ \cite{du2026latencies} & Raw-event attacks with configurable latencies & Related temporal attack setting; constraints and budgets require separate specification. \\
Yu et al.\ \cite{yu2026} & Capacity-one spike-retiming constraints & Protocol reference for the separate classical packet-grid study. \\
Jha et al.\ \cite{jha2025hybrid} & SNN features followed by quantum kernels for EEG & Hybrid temporal classification; distinct from our variational probability readout. \\
Gong et al.\ \cite{gong2024randomized} & Randomized quantum encodings with specified attacker access & Defense assumptions differ from an attack before our classical frontend. \\
Dowling et al.\ \cite{dowling2026guarantees} & Guarantees for specified quantum-classifier scenarios & Motivates assumption-aware interpretation; not a certificate for our timing budgets. \\
This work & End-to-end timestamp attacks on QSNN-v3; separate classical grid controls & Paired computational controls, explicit populations and report-grounded evidence. \\
\hline
\end{tabular}
\end{table*}
```

## 6. تحلیل ریاضی قابل افزودن: state drift، readout و margin

**محل:** یک subsection جدید در پایان بخش Models و پیش از Threat Models. اگر متن اصلی بیش از حد طولانی می‌شود، تعریف و نامساوی اصلی در main و اثبات در supplement قرار گیرد. این تحلیل، استنتاج جبری برای readout مستندشدهٔ مدل است؛ ادعای اندازه‌گیری تازه یا novelty قضیه ندارد.

**پیش‌شرط اجرایی:** بررسی کن سورس واقعاً logits را به صورت affine از probability vector می‌سازد. اگر readout یا ویژگی‌ها در سورس واقعی متفاوت‌اند، این بخش را بدون تطبیق ریاضی درج نکن و اختلاف را گزارش بده. احتمال‌ها باید مربوط به یک measurement ثابتِ مدل آموزش‌دیده باشند. نماد `p` را با polarity رویداد اشتباه نگیر؛ در این بلوک از `q` استفاده شده است.

```latex
\subsection{State distance and classification margin}
\label{sec:margin_interpretation}
For the fixed trained model, let $\rho$ and $\rho'$ denote the clean and retimed quantum states before the fixed readout measurement, and let $q,q'\in\mathbb{R}^{256}$ be the corresponding outcome-probability vectors. Write the logits as $z(q)=Wq+b$, and define the clean pairwise margin against class $k\ne y$ by
\begin{equation}
m_{yk}(q)=(w_y-w_k)^\top q+b_y-b_k.
\end{equation}
Here $y$ is the clean predicted class, equal to the label on the attacked clean-correct subset, and $w_k$ is row $k$ of $W$. Measurement cannot increase trace distance, hence
\begin{equation}
\tfrac12\|q-q'\|_1\leq D_{\mathrm{tr}}(\rho,\rho'),
\qquad
D_{\mathrm{tr}}(\rho,\rho')=\tfrac12\|\rho-\rho'\|_1.
\end{equation}
Combining this inequality with H\"older's inequality gives
\begin{equation}
\begin{split}
m_{yk}(q')\geq m_{yk}(q)
-2\|w_y-w_k\|_\infty D_{\mathrm{tr}}(\rho,\rho').
\end{split}
\label{eq:state_margin}
\end{equation}
Thus a sufficient condition for retaining class $y$ is that the right-hand side remain strictly positive for every $k\ne y$. To see this, subtract the two affine margins and bound the resulting inner product by $\|w_y-w_k\|_\infty\|q'-q\|_1$; positivity of all pairwise margins then preserves the argmax.

This observation separates state displacement from decision failure. A larger state distance need not cause a label change, and a small clean margin can make a smaller displacement consequential. Equation~\eqref{eq:state_margin} is a conditional interpretation of the implemented readout, not a certified timestamp radius: no uniform bound from admissible event retiming through the classical frontend to $D_{\mathrm{tr}}$ has been established here. The final-model campaign also does not report the per-example states needed to evaluate this condition. Its connection to quantum robustness theory is therefore conceptual rather than an application of an existing certificate \cite{dowling2026guarantees}.
```

**کنترل علمی:** ضریب 2 به تعریف trace distance وابسته است و نباید حذف شود. `\|w_y-w_k\|_\infty` حداکثر قدرمطلق مؤلفه‌های اختلاف دو سطر است، نه matrix row-sum norm. اگر دو سطر یکسان‌اند، نامساوی همچنان معتبر است؛ از تقسیم بر این norm بدون بررسی صفر بودن آن خودداری کن. این bound یک شرط کافی است، نه لازم. فقط positivity برای تمام رقبا نتیجهٔ حفظ label می‌دهد. منبع Dowling برای زمینهٔ موضوع است؛ این استنتاج readout-specific را به‌عنوان قضیهٔ نقل‌شدهٔ آن مقاله معرفی نکن.

## 7. تکمیل Results با تحلیل اعداد موجود

**فایل محتمل:** `sections/results.tex`.

### 7.1 پس از پاراگراف p-valueها در Matched timestamp attacks

اگر جمله‌های مشابه قبلاً وجود دارند، آن‌ها را یکپارچه کن تا تکرار ایجاد نشود:

```latex
The paired comparison is driven by discordant examples, not by treating the two ASRs as independent proportions. At the 10\% budget under elapsed-time calibration, the two TEMP-only failures account for the entire numerical difference; there are no PGD-only failures. The exact paired test therefore remains inconclusive at $p=0.5$. At the same budget under candidate or forward matching, the attacks fail on exactly the same three examples. These observations identify a budget-dependent numerical contrast within this fixed population, without establishing a generally stronger attack.
```

### 7.2 پس از نتایج controlled grid

```latex
The integer-grid comparison supplies a particularly clear diagnostic: the custom SNN and spiking ResNet18 differ by only $0.02$ percentage points in clean test accuracy, but by $99.7$ and $97.9$ points in ASR under the two completed budgets. Similar clean accuracy therefore does not summarize the failure profile under this attack recipe. The source of the contrast remains unresolved, because a common recipe does not guarantee comparable optimization strength across architectures. In particular, zero observed successes should be read as failure of the evaluated attack on the selected examples, rather than as a robustness certificate \cite{athalye2018obfuscated,croce2020reliable}.
```

اعداد فوق مشتق مستقیم جدول موجودند: `98.14−98.12=0.02`، `99.9−0.2=99.7`، `98.0−0.1=97.9`. این‌ها آزمایش جدید نیستند. اگر همین تفاضل‌ها قبلاً در متن آمده‌اند، فقط تفسیر تازه را اضافه کن.

### 7.3 روشن‌کردن مخرج ASR در Experimental protocol

در بخش Metrics، نزدیک تعریف ASR، این توضیح را اضافه یا با متن موجود ادغام کن:

```latex
ASR is conditional on the stated clean-correct attack population. Consequently, $1-\mathrm{ASR}$ describes survival under the evaluated attack on that selected population; it is not an unconditional robust accuracy on the full validation or test set. Reusing a joint-correct population improves within-study comparability but changes the estimand relative to evaluation on all examples.
```

از `clean accuracy × (1−ASR)` برای ساخت robust accuracy جدید استفاده نکن: subsetها تصادفی و نمایندهٔ کل correct set نیستند و همهٔ نمونه‌ها نیز حمله نشده‌اند.

## 8. تکمیل Discussion و برنامهٔ آزمایش‌های آینده

**فایل محتمل:** `sections/discussion.tex`. این دو پاراگراف را پس از بحث quantum-specific mechanism اضافه کن یا با پاراگراف موجود ادغام کن:

```latex
\paragraph{Encoding-aware interpretation.}
The quantum component is only one stage of the attacked composition. A feasible timestamp perturbation can change temporal aggregation, spiking summaries, encoded angles and the final probability vector. Without interventions that hold the frontend and training protocol fixed while replacing the readout, the observed failures cannot be attributed uniquely to quantum processing. This distinction complements comparisons of quantum and classical decision geometry \cite{wendlinger2024comparative} and avoids transferring guarantees between incompatible encoding or attacker-access settings \cite{gong2024randomized,dowling2026guarantees}.

\paragraph{Optimization diagnostics.}
The hard-forward, surrogate-backward timestamp pipeline makes attack diagnostics particularly relevant. Gradient checks, alternative surrogates, multiple initializations and gradient-free searches would help distinguish optimizer failure from difficult decision boundaries \cite{athalye2018obfuscated}. The principle of diverse attack evaluation \cite{croce2020reliable} is applicable, but an image-space ensemble cannot be imported unchanged: every candidate must obey the native event constraints or the packet-grid capacity rules. The present candidate and time controls are useful computational comparisons, not evidence that the search has exhausted either feasible set.
```

پاراگراف Next empirical steps فعلی حفظ و با اولویت‌های زیر تکمیل شود. آن‌ها را **planned / future** بنویس، بدون افزودن جدول نتیجهٔ خالی یا ادعای تکمیل:

1. **ارزیابی مستقل:** انتخاب نهایی مدل با validation، سپس QSNN clean/attack روی official test؛ چند seed مستقل frontend و head، همراه شناسهٔ نمونه‌ها و خطای clean هر مدل.
2. **قدرت حمله:** restart، sweep تعداد iteration و step size، lossهای CE و margin، alternate surrogate، derivative-free budget curves؛ ثبت بهترین موفقیت معتبر تا هر بودجه. موفقیت باید با hard forward مجدداً تأیید شود.
3. **کنترل مؤلفهٔ کوانتومی:** frontend، split و بودجهٔ آموزش ثابت، classical head مناسب و capacity-matched، variational head با/بدون entangling gates؛ گزارش parameter count و training cost. این ablation در نسخهٔ فعلی انجام نشده است.
4. **آزمون توضیح state/margin:** ذخیرهٔ state نهایی، probability vector، margin تمیز و margin حمله‌شده برای هر نمونه؛ مقایسهٔ failures و survivors با کنترل realized timestamp distortion و clean margin. از تجمیع میانگین fidelity به‌عنوان اثبات mechanism اجتناب شود.
5. **نظارت و دفاع:** تعریف observables هشت‌کیوبیتی، shot budget، calibration فقط با دادهٔ clean و policy واکنش؛ سپس ROC/PR، false-positive rate و attack تطبیقی. single-qubit marginals جای full-state information را نمی‌گیرند. این نتایج فعلاً موجود نیستند.

جملهٔ پیشنهادی برای پایان Conclusion، پس از حفظ اعداد اصلی:

```latex
The resulting evidence supports a protocol-specific account of end-to-end temporal vulnerability. It also identifies what stronger mechanistic claims would require: independent test evaluation, architecture-aware attack diagnostics, and per-example links between input distortion, quantum-state displacement and classification margin.
```

## 9. منابع افزوده‌شده و BibTeX آماده

هشت منبع زیر **جدید برای bibliography این نسخه** هستند: شش کار 2024 تا 2026 و دو مرجع بنیادی ارزیابی حمله. «جدید برای مقاله» به معنی منتشرشده در امسال نیست. Yu و SPATE از قبل در مقاله‌اند و جزو هشت منبع افزوده محسوب نمی‌شوند. تمام عنوان‌ها و پیوندها در منابع اصلی یا رکورد نویسندگان بررسی شده‌اند؛ جزئیات غیرقطعی را حدس نزن.

| کلید | وضعیت و منبع قابل بررسی | کاربرد و حد ادعا |
|---|---|---|
| `yao2024rawevent` | ECCV 2024؛ [PDF رسمی ECVA](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09164.pdf)، [DOI](https://doi.org/10.1007/978-3-031-73220-1_24) | حمله روی raw events؛ روش آن retiming-only با حفظ دقیق هویت رویدادها نیست. برای دوری از اختلاف سال انتشار proceedings، BibTeX زیر از نسخهٔ رسمی کنفرانس و URL استفاده می‌کند. |
| `du2026latencies` | *Neural Networks* 193، 108026؛ [ناشر](https://www.sciencedirect.com/science/article/pii/S0893608025009062)، [DOI](https://doi.org/10.1016/j.neunet.2025.108026) | latency در raw-event attack؛ online در 2025 و شمارهٔ جلد در 2026. DOI دارای 2025 است و نباید آن را به 2026 تغییر داد. متن کامل ناشر در این بررسی قابل بازیابی نبود؛ ادعای جزئی دربارهٔ optimizer یا constraint اضافه نشود. |
| `jha2025hybrid` | *EPJ Quantum Technology* 12، 130 (2025)؛ [مقالهٔ ناشر](https://link.springer.com/article/10.1140/epjqt/s40507-025-00443-1) | ترکیب featureهای SNN و quantum kernel برای EEG؛ معادل QSNN-v3 نیست. |
| `gong2024randomized` | *Physical Review Research* 6، 023020 (2024)؛ [ناشر](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.6.023020) | randomized encoding و فرض دسترسی مهاجم؛ دفاع اجراشدهٔ این مقاله نیست. |
| `dowling2026guarantees` | *npj Quantum Information* 12، 16 (2026)؛ [رکورد نویسندگان و journal reference](https://arxiv.org/abs/2405.10360v2)، [DOI](https://doi.org/10.1038/s41534-025-01129-3) | تضمین‌ها برای settingهای مشخص؛ certificate برای timestampهای QSNN-v3 نیست. preprint اولیه 2024 است؛ ارجاع ژورنالی 2026. |
| `wendlinger2024comparative` | [preprint نویسندگان، arXiv:2404.16154](https://arxiv.org/abs/2404.16154) | quantum/classical adversarial comparison؛ در این فایل به‌عنوان preprint ارجاع شود، نه ادعای پذیرش قطعی در QCE. |
| `athalye2018obfuscated` | ICML 2018؛ [PMLR 80:274–283](https://proceedings.mlr.press/v80/athalye18a.html) | gradient masking و محدودیت استنتاج robustness از شکست optimizer. |
| `croce2020reliable` | ICML 2020؛ [PMLR 119:2206–2216](https://proceedings.mlr.press/v119/croce20b.html) | ارزیابی متنوع حملات؛ اجرای مستقیم image-space AutoAttack روی رویدادها توصیه یا گزارش نشده است. |

در `references.bib` اضافه کن؛ قبل از درج، موارد تکراری با DOI یا عنوان را merge کن. برای Yao عمداً شمارهٔ جلد و صفحات proceedings درج نشده تا به metadata سال نسخهٔ چاپی وابسته نباشد.

```bibtex
@inproceedings{yao2024rawevent,
  author = {Yao, Yanmeng and Zhao, Xiaohan and Gu, Bin},
  title = {Exploring Vulnerabilities in Spiking Neural Networks: Direct Adversarial Attacks on Raw Event Data},
  booktitle = {Computer Vision -- ECCV 2024},
  year = {2024},
  url = {https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09164.pdf}
}

@article{du2026latencies,
  author = {Du, Xiao and Shi, Wanli and Zhao, Xiaohan and Cao, Yang and Gu, Bin and Wu, Tieru},
  title = {Raw event-based adversarial attacks for {Spiking Neural Networks} with configurable latencies},
  journal = {Neural Networks},
  volume = {193},
  pages = {108026},
  year = {2026},
  doi = {10.1016/j.neunet.2025.108026}
}

@article{jha2025hybrid,
  author = {Jha, Ravi Kumar and Kasabov, Nikola and Bhattacharyya, Saugat and Coyle, Damien and Prasad, Girijesh},
  title = {A hybrid spiking neural network - quantum framework for spatio-temporal data classification: a case study on {EEG} data},
  journal = {EPJ Quantum Technology},
  volume = {12},
  pages = {130},
  year = {2025},
  doi = {10.1140/epjqt/s40507-025-00443-1}
}

@article{gong2024randomized,
  author = {Gong, Weiyuan and Yuan, Dong and Li, Weikang and Deng, Dong-Ling},
  title = {Enhancing quantum adversarial robustness by randomized encodings},
  journal = {Physical Review Research},
  volume = {6},
  pages = {023020},
  year = {2024},
  doi = {10.1103/PhysRevResearch.6.023020}
}

@article{dowling2026guarantees,
  author = {Dowling, Neil and West, Maxwell T. and Southwell, Angus and Nakhl, Azar C. and Sevior, Martin and Usman, Muhammad and Modi, Kavan},
  title = {Adversarial robustness guarantees for quantum classifiers},
  journal = {npj Quantum Information},
  volume = {12},
  pages = {16},
  year = {2026},
  doi = {10.1038/s41534-025-01129-3},
  url = {https://arxiv.org/abs/2405.10360v2}
}

@misc{wendlinger2024comparative,
  author = {Wendlinger, Maximilian and Tscharke, Kilian and Debus, Pascal},
  title = {A Comparative Analysis of Adversarial Robustness for Quantum and Classical Machine Learning Models},
  year = {2024},
  eprint = {2404.16154},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  note = {Preprint},
  url = {https://arxiv.org/abs/2404.16154}
}

@inproceedings{athalye2018obfuscated,
  author = {Athalye, Anish and Carlini, Nicholas and Wagner, David},
  title = {Obfuscated Gradients Give a False Sense of Security: Circumventing Defenses to Adversarial Examples},
  booktitle = {Proceedings of the 35th International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {80},
  pages = {274--283},
  year = {2018},
  publisher = {PMLR},
  url = {https://proceedings.mlr.press/v80/athalye18a.html}
}

@inproceedings{croce2020reliable,
  author = {Croce, Francesco and Hein, Matthias},
  title = {Reliable evaluation of adversarial robustness with an ensemble of diverse parameter-free attacks},
  booktitle = {Proceedings of the 37th International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {119},
  pages = {2206--2216},
  year = {2020},
  publisher = {PMLR},
  url = {https://proceedings.mlr.press/v119/croce20b.html}
}
```

### اصلاح منابع قبلی بدون تغییر پروتکل

- `yu2026`: عنوان کامل موجود حفظ شود. نام نویسندگان مطابق نسخهٔ اصلی: Yi Yu; Qixin Zhang; Shuhan Ye; Xun Lin; Qianshan Wei; Kun Wang; Wenhan Yang; Dacheng Tao; Xudong Jiang. [نسخهٔ پروتکل v1](https://arxiv.org/abs/2602.03284v1). حتی اگر نسخه یا venue جدید پیدا شد، frozen protocol reference: v1 حذف نشود و تنظیمات محلی با نسخهٔ تازه بازنویسی نشوند.
- `spate2026`: Nouhaila Innan; Rachmad Vidya Wicaksana Putra; Muhammad Shafique. [arXiv:2604.11022](https://arxiv.org/abs/2604.11022). عنوان: *SPATE: Spiking-Phase Adaptive Temporal Encoding for Quantum Machine Learning*. preprint بودن حفظ شود مگر ناشر معتبر نسخهٔ نهایی را تأیید کند.
- شناسهٔ repository و commit مبنای داده‌های گزارش‌شده تغییر نکند؛ افزودن منابع جدید نیازمند تغییر snapshot آزمایش نیست.

## 10. شکل‌ها و صفحه‌آرایی

سه شکل اصلی موجود حفظ شوند. شکل علمی تازه با دادهٔ فرضی تولید نکن. برای این نوبت، جدول literature و تحلیل margin از افزودن نمودار تزئینی مفیدترند. فقط اگر شکل pipeline موجود جای مناسبی دارد، برچسب مسیر `timestamps → temporal aggregation → Conv/LIF → angles → quantum probabilities → logits` و محل ورودی حمله را با مدل واقعی هماهنگ کن. این اصلاح شماتیک است، نه نتیجهٔ جدید.

برای جا دادن متن، فونت و فاصله‌ها را غیرمعمول کوچک نکن. اول تکرارهای Results/Discussion را حذف کن؛ در صورت محدودیت venue، جدول مفهومی و اثبات کوتاه به supplement منتقل شوند. متن اصلی باید همچنان مدل، بودجه، population، شمارش موفقیت‌ها و محدودیت اصلی را مستقل توضیح دهد.

## 11. ترتیب اعمال و کنترل نهایی

1. بررسی ساختار واقعی و baseline موجود؛ اگر فقط PDF موجود است، سورس را از project دریافت کن و از حدس‌زدن سورس یا تبدیل خام PDF به مقالهٔ جدید خودداری کن.
2. درج/merge هشت BibTeX، سپس Related Work، جدول و Introduction.
3. تطبیق affine probability readout و درج تحلیل margin؛ سپس تفسیرهای Results و Discussion.
4. حذف تکرارها، تطبیق abstract و conclusion با claims نهایی؛ عددهای abstract با جدول‌ها یکسان بمانند.
5. build با دستور پروژه؛ در صورت استفاده از BibTeX و وجود `latexmk` معمولاً `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` و، اگر منبع مشترک تغییر کرده، `latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex` مناسب است. در پروژهٔ biblatex از backend موجود استفاده کن؛ سبک ارجاع را عوض نکن.
6. undefined citation/reference، duplicate key/label، missing figure، خطای ریاضی و overflow مهم بررسی شوند. جدول سه‌ستونی و معادلهٔ margin را در PDF به‌صورت بصری بررسی کن.
7. کنترل diff: هیچ عدد تجربی، مخرج، p-value، seed، budget یا snapshot بدون سند تغییر نکرده باشد. تعداد منابع نهایی احتمالاً از 9 به 17 می‌رسد؛ فقط اگر bibliography فعلی همان نسخهٔ مبنا باشد و هیچ duplicate وجود نداشته باشد.
8. گزارش بده کدام تغییرها انجام شد، کدام بخش به supplement رفت و آیا build/PDF واقعاً بررسی شد. اگر ابزار build موجود نیست، صریح بنویس؛ ادعای کامپایل موفق نکن.

### متن کوتاه برای ارسال به Codex

> فایل `PAPER_ENRICHMENT_GUIDE.md` را کامل بخوان و روی سورس LaTeX مقاله اعمال کن. بخش‌های الزامی را با حفظ تمام اعداد و حدود شواهد پیاده کن، منابع را بدون تکرار به bibliography اضافه کن، متن و تحلیل آماده را با نمادگذاری پروژه تطبیق بده، سپس main و supplement را کامپایل و PDF را بررسی کن. آزمایش جدید یا نتیجهٔ حدسی نساز. در پایان diff و خلاصهٔ تغییرات و وضعیت واقعی build را بده.
