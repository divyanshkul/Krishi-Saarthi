# **Capital One Launchpad Hackathon: Synopsis**

### **Team Details**

**Team Name:** The Misfits

**Team Members:**

1. Divyansh Kulshreshtha  
2. Siddhant Bharadwaj  
3. Kkrishna Saxena  
4. Harshal Agarwal

---

### **Theme Details**

**Theme Name:** Exploring and Building Agentic AI Solutions for a High-Impact Area of Society: Agriculture

**Theme Benefits:**  
The theme focuses on building ML-AI powered agentic solutions for India's agriculture sector, enabling real-time, hyperlocal, and trustworthy answers across crops, irrigation, weather, markets, and finance. Our solution operates seamlessly in multilingual, low-connectivity environments while intelligently processing noisy public datasets with explainable and reliable outputs. This transforms reactive problem-solving into proactive, risk-aware agricultural intelligence that significantly impacts farmer livelihoods and enables sustainable farming practices across India's diverse agricultural landscape.

---

### **Synopsis**

#### **Solution Overview:**

We are building **Krishi Saarthi**, an agentic AI-powered agricultural advisor that transforms farming decisions for **India's 120 million farmers**. Through intelligent orchestration of specialised AI models, Krishi Saarthi serves as a digital farming companion, **empowering every farmer to maximise their livelihood** with risk-aware, **hyperlocal guidance** across the entire agricultural lifecycle from land preparation to post-harvest market optimization.

Core AI Components:

1. **Low Rank Adaptation (LoRA) fine-tuned Multimodal Vision-Language Model:**  
   1. LoRA fine-tuned VLM for crop disease diagnosis, fertiliser and pest recommendations from on-ground photos.  
   2. Hierarchical pipeline: Fast ResNet classifier with VLM fallback for complex visual reasoning.  
   3. Confidence-based routing ensures reliable field-level decisions.

2. **Kisan Call Center (KCC) Transcript Trained Conversational AI:**  
   1. Instruction fine-tuned on real Kisan Call Centre farmer-expert conversation transcripts  
   2. Multilingual dialogue supporting Hindi-English code-switching with authentic farming communication patterns.

3. **Price Intelligence & Financial Module:**  
   1. LSTM forecasting using real-time mandi price APIs with sell/hold recommendations  
   2. Alternative credit scoring and government scheme matching

Core Product Features:

**Dual Interface:**

1. **Chat Mode**: Voice-first, multimodal interface (text, voice, images)  
2. **Guidance Mode**: Five-stage farming workflow from soil preparation to post-harvest

**Agentic Architecture:**

* Autonomous intent classification for task routing.  
* Dynamic tool orchestration across multimodal vision models, price forecasters, and government scheme matching

**Suicide Intent Classification:**

* Detects distress or self‑harm risk in chat using **intent classifiers** and switches to an empathetic flow.  
* Instantly surfaces verified national/state helplines with one‑tap call/SMS and optional connection to a counsellor.  
* Additionally offers follow‑up links to relevant government relief programs (loan waivers, insurance, financial aid) to address root causes.

**Offline Support for Lack of Internet Access:**

* SMS Chatbot via **Twilio**: When a farmer has no internet, they can simply send an SMS, which Twilio routes to our AI backend, enabling the farmer to chat with the AI advisor entirely over SMS without requiring mobile data.  
* **Local caching** of critical resources for uninterrupted guidance, including storing the latest mandi prices so they remain available if daily updates fail

**Mandi Price Intelligence:**

* **Daily mandi price data** sourced from **data.gov.in**, with **geolocation-based** best‑mandi suggestions, **Long Short-Term Memory (LSTM)** driven short‑term price forecasts for Sell/Hold guidance, and cached last‑known prices with auto‑sync on recovery.

**Share Your Story to the Community: Crowd-sourced self-improvement RAG loop**

* Farmers can share experiences via text/audio/images, the submissions are moderated and stored in a **RAG** knowledge base.  
* With consent, high-value insights inform **periodic model/prompt updates**, continuously improving advice relevance.

**Dynamic YouTube Video Recommendations for farmer upskilling**

* Detects current farming stage from profile, and recent activity  to autonomously recommend relevant Krishi Darshan YouTube videos through semantic matching

**Dailyhunt-Style Agri News & Government Notifications**

* Automated news aggregation using small language models to summarise agricultural news and government notifications into farmer-friendly bullets with extracted eligibility criteria, actionable steps and deadlines.

### **2\. Technical Stack:**

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
   5. Google Cloud Platform (GCP)  for deployment

3. **Mobile Frontend:**  
   1. Flutter, Dart 

#### **3\. Decision Rationale for tech stack:**  In an agricultural context, decisions have real-life consequences. To mitigate risks, we leverage high-quality real-world datasets such as **Agri-LLaVA**(44k instructions) and transcripts from **Kisan Call Center (KCC)** combined with **State of the Art** (SOTA) techniques such as **Instruction Fine-Tuning**, **Parameter Efficient Fine-Tuning** and **SHAP**\-based explainability. These prevent model hallucinations associated with general-purpose **LLMs/MLLMs**, grounding them in facts and nudging the models to be robust as well as accurate in their predictions.

Since many farmers may not have access to laptops, mobile apps offer significant advantages over responsive websites, such as real-time notifications, geolocation-based operations, and better overall performance. Hence, **Flutter** with **Dart** was chosen to enable a single, high-performance codebase targeting both Android and iOS, providing consistent UI/UX and offline-first capability 

To enable the entire operation, our backend infrastructure leverages **Python** with **FastAPI** for the API layer, **PostgreSQL** for structured relational data, **Firebase Firestore** for real-time document storage, with deployment planned on **Google Cloud Platform**. 

#### **4\. Innovation Highlights:**

We have implemented the following novelties in our solution:

1. **Low Rank Adaptation (LoRA)** and **Instruction Fine-tuning** are leveraged to fine-tune the model on an agriculture-specific dataset. These enable us to counteract problems associated with general-purpose LLMs/MLLMs’ close to random performance on domain-specific tasks, such as those demonstrated by Shinoda et al’s Agro Bench at ICCV 2025\. In particular, LoRA opens up the possibility of fine-tuning larger models, which could otherwise be prohibitively expensive and efficient task switching during deployment. The combination of these shows improvement in performance required for handling the risk-intensive nature of the agriculture tasks.

2. Conversational AI Agent trained on [**Kisan Call Center (KCC) transcripts**](https://www.data.gov.in/resource/kisan-call-centre-kcc-transcripts-farmers-queries-answers) of farmer-expert interactions from [data.gov.in](http://data.gov.in) categorised by type (weather, cultural practices, govt schemes, sowing time, etc) and then translates from the regional language answer to English.  
   This curated dataset is then used for domain-specific **instructional fine-tuning** through **adapter** and **prompt-tuning techniques**, enabling the agent to understand farming terminologies, problems faced and their optimal solutions.

3. **In-context Learning** (ICL) is a relatively simple and **computationally inexpensive** technique that enables us to generate agronomist-tailored advisory, disease and pest diagnosis, farm record interpretation, and dialectic adaptation. Features essential for a smooth user experience,

4. Automatic farmer suicide intent classification: our LLM implementation uses **in-context learning** with carefully crafted prompts to detect distress patterns and suicidal ideations in farmer conversations through contextual understanding of Indian agricultural stress indicators, triggering immediate mental health chat support, crisis helpline referrals, and relevant government schemes, including loan waivers and financial assistance programs.

#### 

#### 

#### **5\. Feasibility and User-Friendliness:**  Krishi Saarthi tackles fragmented agricultural data through specialised preprocessing modules using smaller language models to reconstruct incomplete text patterns in government datasets. Additionally, we are planning to integrate Indic models like **AI4Bharat's IndicTrans** to create seamless translation for multilingual, code-switched farmer queries, ensuring natural communication across India's linguistic diversity.

Our fine-tuned VLM and Agri-LLaVA dataset integration addresses hallucination risks by grounding recommendations in verified agricultural imagery and expert-validated responses. This domain-specific training ensures diagnoses stem from established agronomic science. 

The multilingual Flutter app features an intuitive UI/UX design with voice support, SMS fallback for offline scenarios, and quick-access buttons for common farming queries, ensuring seamless adoption across diverse rural user bases.

#### **6\. Success Metrics:**

**Colloquial Queries & Hyperlocal Content**

* ML-related metrics such as accuracy, f1-score, recall, precision, mean squared error, and agriculture visual question answering (VQA) benchmark

* Usability and adaptability across Hindi/English/regional languages and voice interaction success rates

* Single-interaction query resolution rates and offline functionality during network outages

---

### 

### 

### 

### 

### 

### 

### 

### 

### 

### **Methodology/Architecture Diagram**

Below are the 3 main diagrams for our core machine learning flows:

1\. Low Rank Adaptation (LoRA) and Instruction Fine-tuning the Vision-Language Model on agriculture-specific datasets, counteracting general-purpose language models' poor domain performance. It enables cost-effective VLM fine-tuning for agricultural decisions.  
Figma: [https://dub.sh/TheMisfitsVLMFinetuning](https://dub.sh/TheMisfitsVLMFinetuning)

Fig 1: Finetuning a small language model using QLoRA 

2\. The diagram below demonstrates the process used for our **KCC transcript-trained Conversational AI** using prompt tuning with mixed-task batches combining agricultural categories (weather, cultural practices, government schemes) into unified prompts for diverse farming query handling.  
Figma: [https://dub.sh/TheMisfitsPromptTuning](https://dub.sh/TheMisfitsPromptTuning)

Fig 2: Model Tuning vs Prompt Tuning on KCC Transcript Dataset 

3\. The below demonstrates our **Mandi Price Prediction Agent** using data.gov.in APIs and LSTM forecasting. The system employs GPS-based district calculation and profit threshold analysis to generate HOLD/SELL alerts with transport cost approximation for intelligent mandi routing.  
Figma: [https://dub.sh/TheMisfitsMandiPrice](https://dub.sh/TheMisfitsMandiPrice)

Fig 3: Mandi Agent \- Price prediction and recommendations 

---

