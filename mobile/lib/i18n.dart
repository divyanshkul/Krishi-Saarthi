const Map<String, Map<String, String>> translations = {
  'en': {
    'appTitle': 'Krishi Saarthi',
    'chat': 'Chat',
    'guide': 'Guide',
    'mandi': 'Mandi',
    'community': 'Community',
    'askYourQuestion': 'Ask your question...',
    'greeting': 'Namaste! I am your Krishi Saarthi.',
    'yellowLeavesProblem': 'My wheat crop is showing yellow leaves',
    'nitrogenDeficiency':
        'Yellow leaves can be due to nitrogen deficiency. I am looking for a solution for you...',
    'aiAnalysis': 'AI Analysis (95% Confidence):',
    'ureaRecommendation':
        '• Urea: 10 kg/acre\n• Spray with water\n• Improvement will be visible in 7 days',
    'watchVideo': 'Watch Video',
    'talkToExpert': 'Talk to Expert',
    'soilPreparation': 'Soil Preparation',
    'active': 'Active',
    'aiSuggestionDeepPlow':
        'AI Suggestion: Deep plowing is recommended for your area. Moisture level is suitable at 18%.',
    'viewDetailedGuide': 'Detailed Guide',
    'afterHarvest': 'Post-Harvest',
    'storageProcessingMarketing':
        'Storage, processing and marketing strategies',
    'personalizedSuggestions':
        'AI is preparing personalized suggestions for your farm...',
    'wheat': 'Wheat',
    'bhopalMandi': 'Bhopal Mandi',
    'aiSuggestionHold':
        'AI Suggestion: Hold for the next 7 days - 78% probability of price increase.',
    'soybean': 'Soybean',
    'indoreMandi': 'Indore Mandi (45 km)',
    'aiSuggestionSell':
        'AI Suggestion: Sell immediately - decline possible in the next 5 days (82% confidence)',
    '7DayPriceForecast': '7-Day Price Forecast (LSTM Model)',
    'govtSchemes': 'Government Schemes',
    'pmKisan': 'PM-KISAN',
    'pmKisanSubtitle': 'You are eligible · Next installment: 15 December',
    'cropInsurance': 'Crop Insurance Scheme',
    'cropInsuranceSubtitle': 'Application deadline: 30 November',
    'shareYourStory': 'Share Your Story',
    'ramSinghPost': 'Organic manure increased wheat yield by 30% this year!',
    'sunitaDeviPost':
        'There was a problem of leaf curl in tomatoes. AI immediately identified it from the photo and suggested medicine. The crop was saved!',
    'agriNews': 'Agricultural News',
    'mspHike': '5% hike in MSP for Rabi crops',
    'weatherWarning': 'Weather warning for unseasonal rains in Madhya Pradesh',
    
    // Photo and UI strings
    'selectPhotoSource': 'Select Photo Source',
    'choosePhotoMethod': 'Choose how you want to add a photo:',
    'camera': 'Camera',
    'takeNewPhoto': 'Take a new photo',
    'gallery': 'Gallery',
    'chooseFromGallery': 'Choose from gallery',
    'cancel': 'Cancel',
    'justTaken': 'Just taken',
    'photoAttached': 'Photo attached',
    
    // Location and weather
    'bhopalClearWeather': 'Bhopal · Clear Weather',
    'humidity': 'Humidity: 65%',
    'rain': 'Rain: 20%',
    
    // Video recommendations
    'videoRecommendations': 'Video Recommendations',
    
    // Government schemes (updates)
    'pmKisanEligible': 'You are eligible · Next installment: 15th August',
    'cropInsuranceDeadline': 'Application deadline: 30th November',
  },
  'hi': {
    'appTitle': 'कृषि सारथी',
    'chat': 'बात करें',
    'guide': 'गाइड',
    'mandi': 'मंडी',
    'community': 'समुदाय',
    'askYourQuestion': 'अपना सवाल पूछें...',
    'greeting': 'नमस्ते! मैं आपका कृषि सारथी हूँ।',
    'yellowLeavesProblem': 'मेरे गेहूं की फसल में पीले पत्ते दिख रहे हैं',
    'nitrogenDeficiency':
        'पीले पत्ते नाइट्रोजन की कमी के कारण हो सकते हैं। मैं आपके लिए समाधान खोज रहा हूँ...',
    'aiAnalysis': 'AI विश्लेषण (95% विश्वास):',
    'ureaRecommendation':
        '• यूरिया: 10 किलो/एकड़\n• पानी के साथ छिड़काव करें\n• 7 दिन में सुधार दिखेगा',
    'watchVideo': 'वीडियो देखें',
    'talkToExpert': 'विशेषज्ञ से बात करें',
    'soilPreparation': 'मिट्टी की तैयारी',
    'active': 'सक्रिय',
    'aiSuggestionDeepPlow':
        'AI सुझाव: आपके क्षेत्र के लिए गहरी जुताई की सिफारिश। नमी स्तर 18% उपयुक्त है।',
    'viewDetailedGuide': 'विस्तृत गाइड',
    'afterHarvest': 'कटाई के बाद',
    'storageProcessingMarketing': 'भंडारण, प्रसंस्करण और विपणन की रणनीति',
    'personalizedSuggestions':
        'AI आपके खेत के लिए व्यक्तिगत सुझाव तैयार कर रहा है...',
    'wheat': 'गेहूं',
    'bhopalMandi': 'भोपाल मंडी',
    'aiSuggestionHold':
        'AI सुझाव: अगले 7 दिन रुकें - कीमत बढ़ने की 78% संभावना।',
    'soybean': 'सोयाबीन',
    'indoreMandi': 'इंदौर मंडी (45 km)',
    'aiSuggestionSell':
        'AI सुझाव: तुरंत बेचें - अगले 5 दिनों में और गिरावट संभावित (82% विश्वास)',
    '7DayPriceForecast': '7-दिन मूल्य पूर्वानुमान (LSTM Model)',
    'govtSchemes': 'सरकारी योजनाएं',
    'pmKisan': 'PM-KISAN',
    'pmKisanSubtitle': 'आप पात्र हैं · अगली किस्त: 15 दिसंबर',
    'cropInsurance': 'फसल बीमा योजना',
    'cropInsuranceSubtitle': 'आवेदन की अंतिम तिथि: 30 नवंबर',
    'shareYourStory': 'अपनी कहानी साझा करें',
    'ramSinghPost':
        'जैविक खाद से इस साल गेहूं की उपज 30% बढ़ी! AI सारथी के सुझाव बहुत काम आए।',
    'sunitaDeviPost':
        'टमाटर में लीफ कर्ल की समस्या थी। AI ने फोटो से तुरंत पहचान कर दवा बताई। फसल बच गई! 🙏',
    'agriNews': 'कृषि समाचार',
    'mspHike': 'रबी की फसल के लिए MSP में 5% वृद्धि',
    'weatherWarning': 'मध्य प्रदेश में बेमौसम बारिश की चेतावनी',
    
    // Photo and UI strings
    'selectPhotoSource': 'फोटो स्रोत चुनें',
    'choosePhotoMethod': 'आप फोटो कैसे जोड़ना चाहते हैं:',
    'camera': 'कैमरा',
    'takeNewPhoto': 'नई फोटो लें',
    'gallery': 'गैलरी',
    'chooseFromGallery': 'गैलरी से चुनें',
    'cancel': 'रद्द करें',
    'justTaken': 'अभी खींची',
    'photoAttached': 'फोटो जोड़ी गई',
    
    // Location and weather
    'bhopalClearWeather': 'भोपाल · साफ मौसम',
    'humidity': 'नमी: 65%',
    'rain': 'बारिश: 20%',
    
    // Video recommendations
    'videoRecommendations': 'वीडियो सुझाव',
    
    // Government schemes (updates)
    'pmKisanEligible': 'आप पात्र हैं · अगली किस्त: 15 अगस्त',
    'cropInsuranceDeadline': 'आवेदन की अंतिम तिथि: 30 नवंबर',
  },
};
