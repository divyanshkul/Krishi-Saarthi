"""
YouTube video search client.
Simple interface to search for farming videos and return URLs.
"""

from googleapiclient.discovery import build
from typing import Dict, List

class YouTubeClient:
    """Simple YouTube video search client."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube client."""
        self.api_key = api_key
        
        if not api_key or api_key == 'your_youtube_api_key_here':
            raise ValueError("YouTube API key is required. Please configure YOUTUBE_API_KEY.")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            self.enabled = True
        except Exception as e:
            raise ValueError(f"Failed to initialize YouTube client: {e}")
    
    def search_videos(self, keywords: Dict, max_results: int = 10, min_results: int = 3) -> List[Dict]:
        """
        Search for farming videos using generated keywords.
        Ensures minimum 3 videos and maximum 10 videos are returned.
        
        Args:
            keywords: Dict containing primary_keywords, secondary_keywords, search_terms
            max_results: Maximum number of videos to return (capped at 10)
            min_results: Minimum number of videos to return (default 3)
            
        Returns:
            List of video dictionaries with title, url, channel, duration, etc.
        """
        try:
            # Enforce limits
            max_results = min(max_results, 10)
            min_results = max(min_results, 3)
            
            videos = []
            search_terms = self._prepare_search_terms(keywords)
            
            # Search with each term
            results_per_term = max(2, max_results // len(search_terms))
            
            for term in search_terms[:5]:  # Limit to avoid quota exhaustion
                try:
                    term_videos = self._search_single_term(term, results_per_term)
                    videos.extend(term_videos)
                    
                    if len(videos) >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
            # Remove duplicates and filter
            unique_videos = self._remove_duplicates(videos)
            filtered_videos = self._filter_relevant_videos(unique_videos, keywords)
            
            # If we don't have enough videos, try fallback searches
            if len(filtered_videos) < min_results:
                filtered_videos = self._ensure_minimum_videos(filtered_videos, keywords, min_results, max_results)
            
            # Ensure we return between min_results and max_results
            final_videos = filtered_videos[:max_results]
            
            # If still not enough, pad with generic farming videos
            if len(final_videos) < min_results:
                final_videos = self._pad_with_generic_videos(final_videos, min_results)
            
            return final_videos
            
        except Exception as e:
            # Even if search fails, try to return some generic farming videos
            return self._get_fallback_videos(min_results)
    
    def _prepare_search_terms(self, keywords: Dict) -> List[str]:
        """Prepare effective search terms from keywords."""
        search_terms = []
        
        # Use search_terms if available
        if 'search_terms' in keywords:
            search_terms.extend(keywords['search_terms'])
        
        # Use primary keywords
        if 'primary_keywords' in keywords:
            search_terms.extend(keywords['primary_keywords'][:5])
        
        # Fallback to secondary keywords
        if not search_terms and 'secondary_keywords' in keywords:
            search_terms.extend(keywords['secondary_keywords'][:3])
        
        return search_terms[:8]  # Limit search terms
    
    def _search_single_term(self, search_term: str, max_results: int) -> List[Dict]:
        """Search YouTube for a single term."""
        try:
            search_response = self.youtube.search().list(
                q=search_term,
                part='snippet',
                type='video',
                maxResults=max_results,
                order='relevance',
                videoDuration='medium',  # 4-20 minutes
                safeSearch='strict',
                relevanceLanguage='hi'  # Prefer Hindi content
            ).execute()
            
            videos = []
            video_ids = []
            
            # Extract video information
            for item in search_response['items']:
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                
                snippet = item['snippet']
                video_data = {
                    'video_id': video_id,
                    'title': snippet['title'],
                    'channel': snippet['channelTitle'],
                    'description': snippet.get('description', ''),
                    'published_at': snippet['publishedAt'],
                    'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'search_term': search_term
                }
                videos.append(video_data)
            
            # Get additional details (duration, view count)
            if video_ids:
                videos = self._enrich_video_details(videos, video_ids)
            
            return videos
            
        except Exception as e:
            return []
    
    def _enrich_video_details(self, videos: List[Dict], video_ids: List[str]) -> List[Dict]:
        """Enrich videos with additional details like duration."""
        try:
            # Get video statistics and content details
            details_response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # Create lookup dict
            details_lookup = {}
            for item in details_response['items']:
                details_lookup[item['id']] = {
                    'duration': item['contentDetails']['duration'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0))
                }
            
            # Enrich video data
            for video in videos:
                video_id = video['video_id']
                if video_id in details_lookup:
                    details = details_lookup[video_id]
                    video['duration'] = self._parse_duration(details['duration'])
                    video['view_count'] = details['view_count']
                    video['like_count'] = details['like_count']
                else:
                    video['duration'] = 'Unknown'
                    video['view_count'] = 0
                    video['like_count'] = 0
            
            return videos
            
        except Exception as e:
            return videos
    
    def _parse_duration(self, duration_str: str) -> str:
        """Parse YouTube duration format (PT4M20S) to readable format."""
        try:
            duration = duration_str.replace('PT', '')
            
            minutes = 0
            seconds = 0
            
            if 'M' in duration:
                parts = duration.split('M')
                minutes = int(parts[0])
                duration = parts[1] if len(parts) > 1 else ''
            
            if 'S' in duration:
                seconds = int(duration.replace('S', ''))
            
            return f"{minutes}:{seconds:02d}"
            
        except Exception:
            return "Unknown"
    
    def _remove_duplicates(self, videos: List[Dict]) -> List[Dict]:
        """Remove duplicate videos based on video ID."""
        seen_ids = set()
        unique_videos = []
        
        for video in videos:
            video_id = video.get('video_id')
            if video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_videos.append(video)
        
        return unique_videos
    
    def _filter_relevant_videos(self, videos: List[Dict], keywords: Dict) -> List[Dict]:
        """Filter and score videos by relevance to farming."""
        scored_videos = []
        
        for video in videos:
            score = self._calculate_relevance_score(video, keywords)
            if score > 0.3:  # Only include videos with decent relevance
                video['relevance_score'] = score
                scored_videos.append(video)
        
        # Sort by relevance score
        return sorted(scored_videos, key=lambda x: x['relevance_score'], reverse=True)
    
    def _calculate_relevance_score(self, video: Dict, keywords: Dict) -> float:
        """Calculate relevance score for a video."""
        score = 0.0
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        channel = video.get('channel', '').lower()
        
        # Farming-related terms
        farming_terms = [
            'farming', 'agriculture', 'cultivation', 'crop', 'harvest',
            'किसान', 'खेती', 'कृषि', 'फसल', 'बुआई'
        ]
        
        # Check farming relevance
        for term in farming_terms:
            if term in title:
                score += 0.3
            if term in description:
                score += 0.1
            if term in channel:
                score += 0.2
        
        # Check keyword matches
        all_keywords = []
        if 'primary_keywords' in keywords:
            all_keywords.extend(keywords['primary_keywords'])
        if 'secondary_keywords' in keywords:
            all_keywords.extend(keywords['secondary_keywords'])
        
        for keyword in all_keywords[:10]:  # Check top keywords
            keyword_lower = keyword.lower()
            if keyword_lower in title:
                score += 0.2
            if keyword_lower in description:
                score += 0.1
        
        # Quality indicators
        view_count = video.get('view_count', 0)
        if view_count > 10000:
            score += 0.1
        elif view_count > 1000:
            score += 0.05
        
        # Duration preference (5-15 minutes ideal)
        duration_str = video.get('duration', '')
        if ':' in duration_str:
            try:
                minutes = int(duration_str.split(':')[0])
                if 5 <= minutes <= 15:
                    score += 0.1
                elif 3 <= minutes <= 20:
                    score += 0.05
            except:
                pass
        
        return min(score, 1.0)  # Cap at 1.0

    def _ensure_minimum_videos(self, current_videos: List[Dict], keywords: Dict, min_results: int, max_results: int) -> List[Dict]:
        """Ensure we have at least min_results videos by trying fallback searches."""
        if len(current_videos) >= min_results:
            return current_videos
        
        needed_videos = min_results - len(current_videos)
        fallback_videos = []
        
        # Try broader search terms
        fallback_terms = self._get_fallback_search_terms(keywords)
        
        for term in fallback_terms:
            try:
                term_videos = self._search_single_term(term, needed_videos)
                # Filter out duplicates
                for video in term_videos:
                    if not any(v['video_id'] == video['video_id'] for v in current_videos + fallback_videos):
                        fallback_videos.append(video)
                        if len(current_videos) + len(fallback_videos) >= min_results:
                            break
                            
                if len(current_videos) + len(fallback_videos) >= min_results:
                    break
                    
            except Exception:
                continue
        
        return current_videos + fallback_videos[:needed_videos]
    
    def _get_fallback_search_terms(self, keywords: Dict) -> List[str]:
        """Get broader search terms for fallback searches."""
        fallback_terms = [
            "farming techniques",
            "कृषि तकनीक",
            "agriculture farming",
            "crop cultivation",
            "फसल उत्पादन",
            "organic farming",
            "जैविक खेती",
            "sustainable agriculture",
            "modern farming",
            "smart farming"
        ]
        
        # Add crop-specific terms if available
        if 'primary_keywords' in keywords:
            for keyword in keywords['primary_keywords'][:3]:
                fallback_terms.append(f"{keyword} farming")
                fallback_terms.append(f"{keyword} cultivation")
        
        return fallback_terms
    
    def _pad_with_generic_videos(self, current_videos: List[Dict], min_results: int) -> List[Dict]:
        """Pad with generic farming videos if we still don't have enough."""
        if len(current_videos) >= min_results:
            return current_videos
        
        needed_videos = min_results - len(current_videos)
        generic_terms = [
            "basic farming techniques",
            "agriculture for beginners",
            "खेती की बुनियादी बातें"
        ]
        
        generic_videos = []
        for term in generic_terms:
            try:
                term_videos = self._search_single_term(term, needed_videos)
                for video in term_videos:
                    if not any(v['video_id'] == video['video_id'] for v in current_videos + generic_videos):
                        generic_videos.append(video)
                        if len(current_videos) + len(generic_videos) >= min_results:
                            break
                            
                if len(current_videos) + len(generic_videos) >= min_results:
                    break
                    
            except Exception:
                continue
        
        return current_videos + generic_videos[:needed_videos]
    
    def _get_fallback_videos(self, min_results: int) -> List[Dict]:
        """Get fallback videos when all searches fail."""
        # Return a list of curated farming video recommendations
        fallback_videos = []
        
        try:
            # Try to search for very basic farming terms
            basic_terms = ["farming", "agriculture", "कृषि"]
            
            for term in basic_terms:
                try:
                    videos = self._search_single_term(term, min_results)
                    fallback_videos.extend(videos)
                    if len(fallback_videos) >= min_results:
                        break
                except Exception:
                    continue
            
            return fallback_videos[:min_results]
            
        except Exception:
            # If even fallback search fails, return mock videos with educational content
            return self._get_mock_educational_videos(min_results)
    
    def _get_mock_educational_videos(self, count: int) -> List[Dict]:
        """Return mock educational farming videos as last resort."""
        mock_videos = [
            {
                'video_id': 'mock_1',
                'title': 'Basic Farming Techniques for Beginners',
                'channel': 'Agriculture Education',
                'description': 'Learn fundamental farming practices',
                'url': 'https://www.youtube.com/watch?v=mock_1',
                'thumbnail': '',
                'duration': '10:00',
                'view_count': 50000,
                'relevance_score': 0.8,
                'search_term': 'educational'
            },
            {
                'video_id': 'mock_2',
                'title': 'Crop Management and Best Practices',
                'channel': 'Smart Farming',
                'description': 'Modern crop management techniques',
                'url': 'https://www.youtube.com/watch?v=mock_2',
                'thumbnail': '',
                'duration': '12:30',
                'view_count': 30000,
                'relevance_score': 0.7,
                'search_term': 'educational'
            },
            {
                'video_id': 'mock_3',
                'title': 'Sustainable Agriculture Methods',
                'channel': 'Eco Farming',
                'description': 'Environmentally friendly farming practices',
                'url': 'https://www.youtube.com/watch?v=mock_3',
                'thumbnail': '',
                'duration': '8:45',
                'view_count': 25000,
                'relevance_score': 0.6,
                'search_term': 'educational'
            }
        ]
        
        return mock_videos[:count]
