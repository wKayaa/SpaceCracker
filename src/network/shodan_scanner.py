import aiohttp
from typing import List, Dict, Optional
import asyncio

class ShodanScanner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"
        self.queries = [
            'port:2375 "Docker"',
            'port:2376 "Docker"', 
            'port:10250 "kubelet"',
            'port:10255 "kubelet"',
            'port:6443 "kubernetes"',
            '"Docker API" country:US',
            'product:"Docker" port:2375',
            'http.title:"Docker"',
            'port:9200 "elasticsearch"',
            'port:5432 "postgresql"',
            'port:3306 "mysql"',
            'port:27017 "mongodb"',
            'port:6379 "redis"'
        ]
    
    async def search_targets(self, query: str = None, limit: int = 100) -> List[str]:
        """Search for vulnerable targets using Shodan"""
        if not self.api_key:
            return []
            
        targets = []
        search_queries = [query] if query else self.queries
        
        async with aiohttp.ClientSession() as session:
            for search_query in search_queries:
                try:
                    url = f"{self.base_url}/shodan/host/search"
                    params = {
                        'key': self.api_key,
                        'query': search_query,
                        'limit': min(limit, 100)  # Shodan API limit
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for result in data.get('matches', []):
                                ip = result.get('ip_str')
                                port = result.get('port')
                                if ip and port:
                                    target = f"{ip}:{port}"
                                    if target not in targets:
                                        targets.append(target)
                                        
                except Exception as e:
                    continue
                    
                # Rate limiting
                await asyncio.sleep(1)
        
        return list(set(targets))
    
    async def get_host_info(self, ip: str) -> Optional[Dict]:
        """Get detailed host information"""
        if not self.api_key:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/shodan/host/{ip}"
                params = {'key': self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'ip': ip,
                            'ports': data.get('ports', []),
                            'vulns': data.get('vulns', []),
                            'os': data.get('os', 'Unknown'),
                            'hostnames': data.get('hostnames', []),
                            'organization': data.get('org', 'Unknown'),
                            'country': data.get('country_name', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'last_update': data.get('last_update', '')
                        }
        except Exception:
            pass
            
        return None
    
    async def search_docker_targets(self) -> List[str]:
        """Search specifically for Docker API endpoints"""
        docker_queries = [
            'port:2375 "Docker"',
            'port:2376 "Docker"',
            'product:"Docker" port:2375',
            'http.title:"Docker"'
        ]
        
        targets = []
        for query in docker_queries:
            results = await self.search_targets(query, 50)
            targets.extend(results)
        
        return list(set(targets))
    
    async def search_k8s_targets(self) -> List[str]:
        """Search specifically for Kubernetes endpoints"""
        k8s_queries = [
            'port:10250 "kubelet"',
            'port:10255 "kubelet"',
            'port:6443 "kubernetes"',
            'product:"Kubernetes"'
        ]
        
        targets = []
        for query in k8s_queries:
            results = await self.search_targets(query, 50)
            targets.extend(results)
        
        return list(set(targets))
    
    async def search_database_targets(self) -> List[str]:
        """Search for exposed databases"""
        db_queries = [
            'port:5432 "postgresql"',
            'port:3306 "mysql"',
            'port:27017 "mongodb"',
            'port:6379 "redis"',
            'port:9200 "elasticsearch"'
        ]
        
        targets = []
        for query in db_queries:
            results = await self.search_targets(query, 30)
            targets.extend(results)
        
        return list(set(targets))