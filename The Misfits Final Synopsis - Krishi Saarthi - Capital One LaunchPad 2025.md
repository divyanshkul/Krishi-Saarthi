**Krishi Saarthi**  
**Desh ke Kisan ka Digital Saathi**

---

**1\. Team Details**

**Team Name:** The Misfits

**Team Members:**

1. Divyansh Kulshreshtha
2. Harshal Agarwal
3. Kkrishna Saxena
4. Siddhant Bharadwaj

---

**2\. Theme Details**

**Theme Name:** Exploring and Building Agentic AI Solutions for a High-Impact Area of Society: Agriculture

**Theme Benefits:**

The theme focuses on building ML-AI powered agentic solutions for India's agriculture sector, enabling real-time, hyperlocal, and trustworthy answers across crops, irrigation, weather, markets, and finance. Our solution operates seamlessly in multilingual, low-connectivity environments while intelligently processing noisy public datasets with explainable and reliable outputs. This transforms reactive problem-solving into proactive, risk-aware agricultural intelligence that significantly impacts farmer livelihoods and enables sustainable farming practices across India's diverse agricultural landscape.

---

**3\. Synopsis**

**Solution Overview:**

We built **Krishi Saarthi**, a deep agentic AI-powered agricultural advisor that transforms farming decisions for **India's 120 million farmers**. Through intelligent orchestration of specialised AI models powered by SOTA techniques, Krishi Saarthi serves as a digital farming companion, **empowering every farmer to maximise their livelihood** with risk-aware, **hyperlocal guidance** across the entire agricultural lifecycle from land preparation to post-harvest market optimization.

Core AI Components:

1. **Low Rank Adaptation (LoRA) fine-tuned Multimodal Vision-Language Model:**

   1. **LoRA fine-tuned VLM** for crop disease diagnosis, fertilizer and pest recommendations from on-ground photos.

   **Problem:** At a farm, diseases and pests are always manifesting in ways that the farmers might not always be equipped to deal with. Simple search enquiries are either vague or downright incorrect, this is partly because of the following reasons:

   i) Describing pests/diseases in a textual format is inherently hard.

   ii) Image-based search is not yet there when it comes to getting the right answers.

   iii) Search engines do not allow for conversation, even if they manage to fetch the correct results. The farmer has to read through the websites.

   **Naive Solution:** Large Language Models (LLMs), particularly large multimodal models (LMMs), allow for conversations where the user’s input can also contain image/images.

   **Problems with the naive solution:** Despite the extraordinary success of LMMs in the general domain, the challenges associated with applying them to a specific field, such as agriculture in our case, still persist. For instance, recent [AgroBench](https://arxiv.org/abs/2507.20519) at ICCV 2025 found that in some cases, the LMMs performance is as good as random predictions. In scenarios like agriculture, where there are real-life consequences, this solution fails sort of expectations.

   **Our Solution:**

- Method: Instruction Fine-Tuning: Zhou et al in [LIMA: Less is More for Alignment](https://arxiv.org/abs/2305.11206), and Wei et al in [Finetuned Language Models Are Zero-Shot learners](https://arxiv.org/abs/2109.01652) show that instruction fine-tuning aligns LLMs with human intent, effectively enhancing the model’s zero-shot and few-shot learning capability. The alignment is an important step in making sure the model understands the intent of the end users, in essence, ensuring the model serves its intended purpose.
- Dataset/s utilised: [Agri-LLava](https://arxiv.org/abs/2412.02158) is an instruction fine-tuning dataset covering over 221 types of pests and diseases with approximately 400,000 data entries. Unlike standard Instruction fine-tuning datasets, which consist of Q/A pairs, this is a conversational style dataset mimicking the manner in which these models would be used in real life.

**Problems faced:** Fine-tuning of any kind is expensive and not possible on consumer GPUs

**Our Solution:**

- **QLoRA:** We utilise [QLoRA](https://arxiv.org/abs/2305.14314) to overcome compute-related challenges associated with the large in LLMs, number of parameters. Quantization aims to reduce the precision of a model’s parameter from higher bit-widths (like 32-bit floating point) to lower bit-widths (like 8-bit integers), thus speeding up inference. QLoRA brings LoRA (Low Rank Adaptation) to the quantised world. In brief, the method identifies the weights that count the most and only fine-tunes those; for example, we fine-tune only \<1% parameters of the 2.2 B SmolVLM-base. This class of methods also prevent catastrophic forgetting, ensuring the model doesn’t forget its original knowledge in the process of fine-tuning.

**Our approach in a nutshell:**

Fig. 1: Finetuning a Small Language Model using QLoRA

Figma: [https://dub.sh/TheMisfitsQLoRAFineTuning](https://www.figma.com/board/1glLIvtWobOdWcPypQ1GjU/Krishi-Saarthi---Finetuning-a-SLM-using-QLoRA?node-id=0-1&t=6Hk2tzIBBqUneazg-1)

**Our solution in action:**  
Fig. 2: Difference between Original SmolVLM and Our Instruction Fine-tuned VLM’s output

2. **Kisan Call Center (KCC) Transcript Trained Conversational AI:**

   1. Instruction fine-tuned on real Kisan Call Centre farmer-expert conversation transcripts
   2. Multilingual dialogue supporting Hindi-English code-switching with authentic farming communication patterns.

**Problem:** Farming is an involved process where the more creative farmers intend to apply their brains to improve the yield. To tread the non-conventional path requires access to information that is difficult to find, such as information about crop varieties, cultural practices, weather and more.

**Our solution:**

- **Dataset:** On January 21, 2004, the Ministry of Agriculture launched Kisan Call Centres to facilitate answering farmers’ queries in their own dialect. The government maintains meticulous transcripts of these calls.
- **Replicating how KCC works in real world:** Queries are first categorised and then forwarded to those well-versed in the field. We replicate this in a computationally inexpensive way through the recent advancements in pre-fix tuning, whereby virtual tokens are added to the existing LLM model. These tokens help the model take up a persona, what separates them from the standard hard system prompts, like “You are an agriculture expert”, is that these do not suffer from the prompt sensitivity problems as demonstrated in Chatterjee et al. where LLMs are found to be sensitive to minor variations in prompts, such as spelling errors, alteration of wording or prompt template. These are appendable prompts that we learn by training the model on the KCC dataset.

**Problems faced:** The dataset is noisy, and sometimes the LLM might hallucinate and give wrong outputs

**Our solution:**

- The dataset contains in the Query Text columns, queries that are too vague and sometimes the same query is used for different answers. We make use of GPT-4 to reverse engineer the queries from the answer so that they reflect the true nature of the query for which the farmer reached out to KCC. This ensures that after prefix tuning the model is able to generate relevant outputs. The KCC answers are also in the primary language of the state in which they took place; we use Machine Translation to translate all of them to English. This helps us to later operate the conversational AI tool according to the purpose of KCC, “Answering Farmers’ Queries in Their Own Language”. The Machine Translation approach enables us to handle code-switch, use of colloquial language etc, in a smooth fashion going forward.
- Even with domain-specific fine-tuning, the risk of model hallucination remains, while it helps the model get the persona, the model can still make up things. To handle edge cases such as these, we ground the answer in facts by utilising Gemini’s Google Search Grounding. The final model’s output is a kind of in-context learning, where the Google Search enabled Gemini’s output is synthesised with our prefix tuned LLM (TinyLLama in our case)
- To store multiple specialist models is hard, so we utilise prefix tuning whereby, depending on the query, the model picks up the virtual token associated with the category, similar to how a fertiliser query will get redirected to the fertiliser department.

Figma: [https://dub.sh/TheMisfitsPromptTuning](https://dub.sh/TheMisfitsPromptTuning)

Fig. 3: Model Tuning vs Prompt Tuning on KCC Transcript Dataset

3. **Price Intelligence & Financial Module:**  
   **Problem:** There is a lot of variability associated with mandi market prices, this makes it tough for the farmer to decide whether to hold/sell  
   **Our Solution:**

- **Dataset:** We use a dataset of Mandi Prices collected from 2001, these prices are collected across states and crops, making the dataset a valuable resource for the purpose of training a time-series-based prediction model.
- We train a Long Short-Term Memory (LSTM) network, which uses the dataset of the previous 30 days to predict the Min, Modal, and Max price. Depending on the predictions, we also identify the best days to sell and hold.

**Core Product Features**

**Dual Interface:**

1. **Chat Mode**: Voice-first, multimodal interface (text, voice, and image)

   At the heart of **Krishi Saarthi** lies **DHARTI** – **\*D**ecision **H**ub for **A**gentic **R**outing & **T**ask **I**ntegration\* – our master agent that intelligently orchestrates farmer interactions. Acting as the first point of contact, DHARTI ensures every query is accurately understood, pre-processed, and routed to the most suitable specialized agent.

   **Supported Input Formats**

   The chatbot provides a **multimodal interface**, reflecting the real-world diversity of farmer communication:

1. **Text Queries** – Farmers can directly type questions in their preferred language.
1. **Image \+ Text** – Field images (e.g., diseased crops, pest damage, soil conditions) combined with short descriptions.
1. **Voice Recording** – Farmers can simply speak their query in their local dialect/language.

**DHARTI’s Processing Pipeline**

- **Text Input** → Passed to DHARTI for _intent classification_ and routing.
- **Image Input** → Directly forwarded to the **Vision-Language Model (VLM)** fine-tuned for agricultural use cases like crop disease detection, fertilizer guidance, and pest identification.
- **Voice Input** → Pre-processed through a three-step pipeline:

  1. **Transcription** of the .wav file.
  2. **Language transcription** using GPT4o transcribe **& Translation** using GPT4o
  3. **Intent Classification** to select the right agent.

  **Agentic Routing by DHARTI**

Once input is normalised, DHARTI routes the query to the most relevant **Krishi Saarthi Agent**:

- **Govt Scheme Recommender RAG** → It uses semantic search and AI generation to match farmer queries with 50+ central and state schemes. It provides guidance by retrieving relevant schemes and explaining eligibility, benefits, and application steps with URL to the relevant website.
- **Kisan Call Centre Transcript Agent** → For common queries (crop practices, weather, irrigation, pest management), leveraging fine-tuned KCC conversational data.
- **SOS Mode** → If DHARTI detects depressive or suicidal intent, it escalates to **mental health support**, surfacing crisis helplines, loan relief programs, and immediate guidance.

**Why DHARTI Matters**

By functioning as a **decision-making orchestrator**, DHARTI makes Krishi Saarthi:

- **Context-Aware**: Understanding text, image, or voice seamlessly.
- **Farmer-Centric**: Bridging the gap between query and action without forcing farmers into rigid input modes. Ideal for even those with limited technical literacy.
- **Safe & Responsible**: Proactively detecting distress signals to protect farmer well-being.

Fig. 4: Overview of our deep agent, DHARTI, which routes the query to the specialised sub-agent and tools

2. **Guidance Mode**: Five-stage farming workflow from soil preparation to post-harvest  
   **Problem:** Farming is a complex, multi-stage process where farmers often struggle with timing decisions, stage-specific practices, and sequential planning from soil preparation to post-harvest. Traditional agricultural guidance is either too generic or fails to provide step-by-step, stage-aware recommendations that align with the actual farming lifecycle. Farmers need structured, progressive guidance that evolves with their crop's development stages  
   **Naive Solution:** A simple farming calendar or generic checklist that provides the same advice to all farmers regardless of their specific crop, location, soil conditions, or current farming stage.  
   **Problems with the Naive Solution:**

- No Stage Awareness: Generic calendars don't account for actual crop development stages or regional variations
- Lack of Personalisation: Same advice for all farmers regardless of their specific conditions, crop varieties, or local practices
- No Progressive Learning: Farmers miss the interconnected nature of farming stages and how decisions in one stage affect subsequent ones
- Static Information: No adaptation based on real-time conditions, weather patterns, or emerging challenges
  **Our Solution:**  
  **Method:** Intelligent Workflow Orchestration with Stage-Aware AI Guidance \- We implement a comprehensive five-stage farming workflow that combines agentic AI routing with progressive agricultural guidance. Our system understands where farmers are in their farming journey and provides contextually appropriate, stage-specific recommendations.
  **The Five-Stage Workflow:**
- Soil Preparation & Land Management
- Sowing & Plantation
- Crop Care & Management
- Harvesting
- Post-Harvest & Marketing

![][image1]![][image2]![][image3]![][image4]![][image5]

arious stages of guided modes of Krishi Saarthi

**Stage Detection & Routing:** Our DHARTI agent automatically detects the farmer's current stage based on:

- Crop registration data (sowing date, crop type, location)
- LLM-powered stage analysis using days since sowing and regional growing patterns
- Visual confirmation through uploaded field images
- Farmer's explicit stage selection or query context
- Progressive Guidance Pipeline:

  **Smart Transitions:** The system proactively suggests when farmers should transition between stages based on:

- Crop development indicators
- Weather patterns and seasonal timing
- Regional farming practices
- Individual farm progress tracking  
  **Multilingual & Multimodal Support**: Each stage supports:
- Voice Queries: "Mere kheton mein ab kya karna chahiye?" (What should I do in my fields now?)
- Image Analysis: Upload field photos for stage-specific visual assessment
- Text Guidance: Detailed, step-by-step instructions in Hindi/English
  **Why Guided Mode Matters:**  
  By providing structured, progressive agricultural guidance, Guided Mode transforms farming from reactive problem-solving into proactive, informed decision-making. Farmers gain confidence through clear next steps, reduce risks through stage-appropriate timing, and maximize yields through scientifically-backed, contextually-relevant recommendations that evolve with their crop's development.

**Agentic Architecture:**

Fig. 6: Krishi Saarthi Project Architecture

Figma: [https://dub.sh/TheMisfitsArchitecture](https://www.figma.com/board/kmqJoTidOVrBUORQVeXrOh/Krishi-Saarthi---The-Misfits?node-id=0-1&p=f&t=XYIwNI1x38Uj8tKi-0)

- Autonomous intent classification for task routing.
- Dynamic tool orchestration across multimodal vision models, price forecasters, and government scheme matching.

**Suicide Intent Classification:**

- At least 112,000 people working in the agricultural sector have committed suicide in the past decade in India, according to data by the National Crime Record Bureau. This remains an important India specific problem.
- Detects distress or self‑harm risk in chat using **intent classifiers** and switches to an empathetic flow.
- Instantly surfaces verified national/state helplines with one‑tap call/SMS and optional connection to a counsellor.
- Additionally offers follow‑up links to relevant government relief programs (loan waivers, insurance, financial aid) to address root causes.

Fig. 7: Our Suicide Intent Classification agent in action

**Offline Support for Lack of Internet Access:**

- **Voice Call** Query to **SMS** Reply \- A **Twilio**\-powered system has been established to enable farmers **without internet connectivity** to place voice calls to our dedicated endpoint and receive AI-generated responses to their agricultural queries via SMS.
- The workflow involves capturing and recording the farmer's spoken query, converting the audio to text through transcription and translation services, feeding the processed input to our DHARTI Agent for analysis, and finally transmitting the AI-generated agricultural guidance to the caller as an SMS response.

Figma: [https://dub.sh/TheMisfitsTwilio](https://www.figma.com/board/oUKR1sCfRf1lMDWHkDEliG/TwilioOfflineArchitecture?node-id=0-1&t=RzWjfty2qf6ve9oJ-1)

Fig. 8: Twilio based Offline System Architecture

**Mandi Price Intelligence:**

- The Price Intelligence & Financial Module applies LSTM forecasting with real-time mandi price APIs to guide farmers on sell/hold decisions. Using mandi price data since 2001, the model analyses the past 30 days to predict min, modal, and max prices, recommending optimal selling days to maximise profits and minimise risks.

**Government Scheme Recommender RAG Agent Problem**: Indian farmers face significant barriers accessing 100+ government agricultural schemes due to fragmented information, complex language, and a lack of personalised guidance, missing of crucial financial assistance opportunities.

**Naive Solution**: Simple keyword-based search engines require farmers to manually browse hundreds of schemes and decipher complex eligibility criteria themselves.

**Problems with the Naive Solution**:

- Information Overload: Farmers get overwhelmed by irrelevant schemes
- Language Barriers: Bureaucratic language makes schemes incomprehensible
- No Personalisation: Generic listings don't consider individual farmer circumstances
- Discovery Gap: Relevant schemes remain hidden due to poor search capabilities

**Our Solution**:

**Method**: We implement a sophisticated RAG system combining semantic search with AI-powered generation, understanding farmer intent through semantic embeddings to provide personalised, actionable advice.

**Dataset Utilised**: Comprehensive scheme data scraped from MyScheme.gov.in covering 100+ agricultural schemes (492 document chunks), converted into 768-dimensional vectors using Google's embedding-001 model.

**Advanced Ranking Algorithm**: Hybrid scoring system combining base semantic similarity, title matching boost, and intelligent aggregation for maximum relevance.

**Cloud-Native Architecture**: Google Cloud-based approach ensuring zero cold start, scalable performance, and superior multilingual support for Hindi-English code-switching.

**RAG Generation Pipeline**: Google Gemini 2.0 Flash transforms retrieved information into farmer-friendly advice with eligibility assessment, benefit calculations, and step-by-step application guidance.

**Our Approach in Action:**

| Farmer Query: "I don't have storage, any schemes for godown?" |
| :-----------------------------------------------------------: |

↓

| Vector Embedding (768-dim) → Semantic Search (492 documents) |
| :----------------------------------------------------------: |

↓

| Retrieved: "Construction of Godown for Grain Storage" (Score: 0.880) |
| :------------------------------------------------------------------: |

↓

| Gemini Generation → Personalized advice with eligibility, benefits, next steps |
| :----------------------------------------------------------------------------: |

**Dynamic YouTube Video Recommendations**

**Problem:** Farmers struggle to find timely, relevant agricultural videos on YouTube due to generic searches yielding overwhelming, irrelevant results that don't match specific crops, growth stages, or local conditions.

**Naive Solution:** Simple search bar querying YouTube API with basic crop names like "wheat farming."

**Problems with the Naive Solution:**

- **Lack of Context:** Not stage-aware \- flowering crop farmers get irrelevant sowing videos
- **Information Overload:** Returns thousands of generic, low-quality videos
- **Not Hyperlocal:** Ignores critical regional farming variations
- **Reactive, Not Proactive:** Requires manual search instead of timely recommendations

**Our Solution:** Engineered agentic pipeline delivering proactive, hyper-contextual video recommendations through specialised agents.

**Method:** Autonomous system orchestrating multiple agents to transform farmer data into curated video playlists.

**Contextual Trigger & Data Ingestion:** Automatically pulls farmer's crop data (type, sowing date, location) from the Firebase Firestore database.

**LLM-Powered Stage Detection:** Uses gemini-2.5-flash to calculate days since sowing and accurately determine precise physiological stage (e.g., "Tillering Stage," "Grain Filling").

**Dynamic, Multilingual Keyword Generation:** Generates rich, specific multilingual (English/Hindi) search keywords like "wheat tillering stage nutrient management" and "गेहूं में कल्ले बढ़ाने के उपाय."

**Intelligent YouTube Search & Relevance Filtering:** Queries YouTube API with precise keywords, then applies custom relevance scoring algorithm filtering by title, description, and channel authority for high-quality recommendations.

Figma: [https://dub.sh/TheMisfitsYoutubeRecommendation](https://www.figma.com/board/fUmzfp3IHJ8yat8d9PSP3N/Krishi-Saarthi---Profile-based-youtube-recommendation-system?node-id=0-1&t=tOJxUxdfhsbGgpdW-1)

Fig. 9: Overview of profile-based YouTube recommendation system

**Our Approach in a Nutshell:** Our pipeline transforms a simple farmer profile into a powerful recommendation engine, ensuring the right video finds the right farmer at the right time.

Farmer Profile (Firebase) → LLM-Powered Crop Stage Detection → Dynamic Multilingual Keyword Generation (LLM) → Intelligent YouTube Search & Relevance Ranking → Hyper-Contextual Video Recommendations

**Our Solution in Action:** Consider a farmer in Indore, Madhya Pradesh, who planted soybeans 108 days ago.

- **Trigger:** The system retrieves this data from Firebase.
- **Stage Detection:** The LLM agent analyzes the context and determines the crop stage is "Maturity/Harvest Ready."
- **Keyword Generation:** The keyword agent generates specific terms like "soybean harvesting techniques Madhya Pradesh," "सोयाबीन की कटाई," and "how to check soybean moisture content for harvest."
- **Recommendation:** Instead of a generic video on "soybean farming," the farmer is proactively shown a highly relevant video titled "Soybean Harvesting: How to check moisture and prevent shatter loss" from a trusted agricultural channel, delivered in their preferred language.

**Share Your Story to the Community: Crowd-sourced self-improvement RAG loop**

- Farmers can share experiences via text/audio/images, the submissions are moderated and stored in a **RAG** knowledge base.
- With consent, high-value insights inform **periodic model/prompt updates**, continuously improving advice relevance.

---

**Technical Stack**

1. **Machine Learning:**

   1. Hugging Face
      1. Transformers
      2. PEFT, SFT
   2. BitsAndBytes (for model quantization)
   3. vLLM
   4. PyTorch
   5. LangChain, LangGraph
   6. Gemini / OpenAI API
   7. Numpy, Pandas, Weights and Biases, Scikit-learn, SHAP, and Matplotlib

2. **Backend:**

   1. Python, FastAPI
   2. PostgreSQL
   3. Twilio API
   4. Firebase Firestore
   5. Google Cloud Platform (GCP) for deployment

3. **Mobile Frontend:**
   1. Flutter, Dart

#### **Decision Rationale for tech stack:**

In an agricultural context, decisions have real-life consequences. To mitigate risks, we leverage high-quality real-world datasets such as **Agri-LLaVA**(44k instructions) and transcripts from **Kisan Call Center (KCC)** combined with **State of the Art** (SOTA) techniques such as **Instruction Fine-Tuning**, **Parameter Efficient Fine-Tuning** and **SHAP**\-based explainability. These prevent model hallucinations associated with general-purpose **LLMs/MLLMs**, grounding them in facts and nudging the models to be robust as well as accurate in their predictions.

Since many farmers may not have access to laptops, mobile apps offer significant advantages over responsive websites, such as real-time notifications, geolocation-based operations, and better overall performance. Hence, **Flutter** with **Dart** was chosen to enable a single, high-performance codebase targeting both Android and iOS, providing consistent UI/UX and offline-first capability

To enable the entire operation, our backend infrastructure leverages **Python** with **FastAPI** for the API layer, **PostgreSQL** for structured relational data, **Firebase Firestore** for real-time document storage, with deployment planned on **Google Cloud Platform**.

---

####

#### **Innovation Highlights**

We have implemented the following novelties in our solution:

1. **Low Rank Adaptation (LoRA)** and **Instruction Fine-tuning** are leveraged to fine-tune the model on an agriculture-specific dataset. These enable us to counteract problems associated with general-purpose LLMs/MLLMs’ close to random performance on domain-specific tasks, such as those demonstrated by Shinoda et al’s Agro Bench at ICCV 2025\. In particular, LoRA opens up the possibility of fine-tuning larger models, which could otherwise be prohibitively expensive and efficient task switching during deployment. The combination of these shows improvement in performance required for handling the risk-intensive nature of the agriculture tasks.

2. Conversational AI Agent trained on [**Kisan Call Center (KCC) transcripts**](https://www.data.gov.in/resource/kisan-call-centre-kcc-transcripts-farmers-queries-answers) of farmer-expert interactions from [data.gov.in](http://data.gov.in) categorised by type (weather, cultural practices, govt schemes, sowing time, etc) and then translates from the regional language answer to English.  
   This curated dataset is then used for domain-specific **instructional fine-tuning** through **adapter** and **prompt-tuning techniques**, enabling the agent to understand farming terminologies, problems faced and their optimal solutions.

3. **In-context Learning** (ICL) is a relatively simple and **computationally inexpensive** technique that enables us to generate agronomist-tailored advisory, disease and pest diagnosis, farm record interpretation, and dialectic adaptation. Features essential for a smooth user experience,

4. Automatic farmer suicide intent classification: our LLM implementation uses **in-context learning** with carefully crafted prompts to detect distress patterns and suicidal ideations in farmer conversations through contextual understanding of Indian agricultural stress indicators, triggering immediate mental health chat support, crisis helpline referrals, and relevant government schemes, including loan waivers and financial assistance programs.

---

#### **Feasibility and User-Friendliness**

Krishi Saarthi tackles fragmented agricultural data through specialised preprocessing modules using smaller language models to reconstruct incomplete text patterns in government datasets. Additionally, we integrated Machine Translation and proprietary LLMs to create seamless translation for multilingual, code-switched farmer queries, ensuring natural communication across India's linguistic diversity.

Our fine-tuned VLM and Agri-LLaVA dataset integration addresses hallucination risks by grounding recommendations in verified agricultural imagery and expert-validated responses. This domain-specific training ensures diagnoses stem from established agronomic science.

The multilingual Flutter app features an intuitive UI/UX design with voice support, SMS fallback for offline scenarios, and quick-access buttons for common farming queries, ensuring seamless adoption across diverse rural user bases.

---

####

#### **Success Metrics**

**Colloquial Queries & Hyperlocal Content**

- ML-related metrics such as accuracy, f1-score, recall, precision, mean squared error, agriculture visual question answering (VQA) benchmark, and comparison between default vs fine-tuned model.

- Usability and adaptability across Hindi/English/regional languages and voice interaction success rates

- Single-interaction query resolution rates and offline functionality during network outages

---

### **Problems We Tackled and How At A Glance**

i) Addressing specific prevalent constraints:

- Understand local, natural-language queries: We make use of Machine Translation and GPT4o to ensure that even when working with low-resource Indian languages, the user has a seamless user experience. Additionally, the government-sourced datasets used to fine-tune our models contain data specific to otherwise underrepresented contexts.
- Synthesize insights across domains: Our Deep Agentic solution uses a network of sub-agents that leverage SOTA techniques and publicly sourced datasets to gather insights: QLoRA \+ Quantization \+ Instruction-FineTuning Conversational Agriculture Dataset (pest science), Prefix Tuning \+ KCC transcripts Google Search Grounding \+ Incontext Learning (crop cycles), and Government Scheme RAG \+ Large Language Model (Finance)
- Infer meaning, adapt to context, and explain it answers: We combine LLMs trained for general-purpose tasks with specialised models in an agentic workflow, enabling our models to understand what is being asked, adapt to the context, use verified sources to check, to provide easily understandable to the point output.
- Be usable by someone with low digital access but high decision responsibility: All of our agents’ components are accessible by calling a number without requiring any internet access whatsoever. In addition, when the internet is available, a person can communicate in any of the Indian Languages through either voice or text. The responses of our model are vetted at multiple instances by verified sources on the internet and specialised models, ensuring the saarthi gives the right guidance.

ii) Problems we tackled on the way to building Krishi Saarthi:

- Noisy, incomplete, non-standard datasets: Government source datasets are unstructured and noisy. For example, the KCC transcript: Exhibit A: It contains answers in local language, we translate them to English so the insights are transferred throughout the country. Exhibit B: It contains imprecise question descriptions; we use proprietary LLMs to reverse engineer the queries. For the market price prediction, the data contains statistical inconsistencies, which are resolved using classical data-driven decision-making techniques.
- Multilingual, code-switched, colloquial questions: We use Machine Translation and SOTA audio transcription models to bridge the gap with the primary language in which our specialised models are trained. This allows us to be robust to issues arising in a multilingual context.
- Hallucination risks in LLMs and grounding in facts: Recognising the risks associated with using off-the-shelf LLMs, we train our model on large-scale datasets and use Google Search grounding to synthesise their responses. For instance, a 400k instructional conversational style dataset is used to power our model for pest and disease-related queries.
- Design for reliability, explainability, trust, and real-world edge cases: Our system employs a multiple-model setup, grounded with Google Search and verified sources, to ensure outputs remain reliable, explainable, and trustworthy. To enhance transparency, we prompt the model to provide multiple options wherever applicable, reducing over-reliance on a single response. We further integrate state-of-the-art methods such as SHAP (SHapley Additive exPlanations), which leverage cooperative game theory to explain model outcomes in a rigorous, interpretable manner. Importantly, our design incorporates real-world edge cases, particularly in domains where errors carry significant costs, ensuring that the system is both robust and dependable in high-stakes scenarios.

---

**Citations**

- Jason Wei, Maarten Bosma, Vincent Y Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M Dai, and Quoc V Le. Finetuned language models are zero-shot learners. arXiv preprint arXiv:2109.01652, 2021 cite this
- Shinoda, R., Inoue, N., Kataoka, H., Onishi, M., & Ushiku, Y. (2025). AgroBench: Vision-Language Model Benchmark in Agriculture. _ArXiv_. [https://arxiv.org/abs/2507.20519](https://arxiv.org/abs/2507.20519)
- Li, X. L., & Liang, P. (2020). Prefix-Tuning: Optimizing Continuous Prompts for Generation. ArXiv. [https://arxiv.org/abs/2101.00190](https://arxiv.org/abs/2101.00190)
- Wang, L., Jin, T., Yang, J., Leonardis, A., Wang, F., & Zheng, F. (2024). Agri-LLaVA: Knowledge-Infused Large Multimodal Assistant on Agricultural Pests and Diseases. ArXiv. [https://arxiv.org/abs/2412.02158](https://arxiv.org/abs/2412.02158)
- Lundberg, S., & Lee, S. (2017). A Unified Approach to Interpreting Model Predictions. ArXiv. [https://arxiv.org/abs/1705.07874](https://arxiv.org/abs/1705.07874)
- Dong, Q., Li, L., Dai, D., Zheng, C., Ma, J., Li, R., Xia, H., Xu, J., Wu, Z., Liu, T., Chang, B., Sun, X., Li, L., & Sui, Z. (2022). A Survey on In-context Learning. ArXiv. [https://arxiv.org/abs/2301.00234](https://arxiv.org/abs/2301.00234)
- Hu, E. J., Shen, Y., Wallis, P., Li, Y., Wang, S., Wang, L., & Chen, W. (2021). LoRA: Low-Rank Adaptation of Large Language Models. ArXiv. [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
- Zhou, C., Wang, H., Yuan, X., Yu, Z., & Bu, J. (2024). Less is More : A Closer Look at Multi-Modal Few-Shot Learning. ArXiv. [https://arxiv.org/abs/2401.05010](https://arxiv.org/abs/2401.05010)
- Nawaz, U., Zaheer, M. Z., Khan, F. S., Cholakkal, H., Khan, S., & Anwer, R. M. (2025). AI in Agriculture: A Survey of Deep Learning Techniques for Crops, Fisheries and Livestock. ArXiv. [https://arxiv.org/abs/2507.22101](https://arxiv.org/abs/2507.22101)
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. ArXiv. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
- Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. ArXiv. [https://arxiv.org/abs/2305.14314](https://arxiv.org/abs/2305.14314)
- M. Grootendorst, “A Visual Guide to Quantization: Demystifying the Compression of Large Language Models,” Exploring Language Models (newsletter), Jul. 22, 2024
  Available: https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization

[image1]: data:image/png;base64,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
[image2]: data:image/png;base64,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
[image3]: data:image/png;base64,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
[image4]: data:image/png;base64,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
[image5]: data:image/png;base64,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
