import os
import re
import csv

def generate_endpoints():
    api_dir = 'worldmonitor/api'
    rows = []
    
    for root, dirs, files in os.walk(api_dir):
        for f in files:
            if f.endswith(('.ts', '.js')) and not f.endswith(('.test.ts', '.test.js', '.test.mjs', '.d.ts')) and not f.startswith('_'):
                rel = os.path.relpath(os.path.join(root, f), api_dir).replace('\\', '/')
                endpoint_name = '/api/' + rel.replace('.ts', '').replace('.js', '')
                path = os.path.join(root, f)
                try:
                    content = open(path, 'r', encoding='utf-8', errors='ignore').read()
                except Exception:
                    content = ''
                
                methods = []
                for m in ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']:
                    if re.search(r'\b' + m + r'\b', content):
                        methods.append(m)
                
                auth_needed = 'Yes' if any(k in content for k in ['validateApiKey', 'validateBearerToken', 'resolvePremiumCallerIdentity', 'checkTierProEntitlement', 'RELAY_SHARED_SECRET', 'requireAuth']) else 'No'
                takes_params = 'Yes' if any(p in content for p in ['searchParams', 'req.json()', 'req.body', 'URLSearchParams', 'feedUrl', 'url']) else 'No'
                returns_user_data = 'Yes' if any(u in content for u in ['userId', 'userPrefs', 'session', 'account', 'customer', 'clerk', 'token']) else 'No'
                
                rows.append({
                    'Method': '/'.join(methods) if methods else 'GET',
                    'Path': endpoint_name,
                    'Auth Needed?': auth_needed,
                    'Takes URL/Param?': takes_params,
                    'Returns User Data?': returns_user_data
                })
                
    rows.sort(key=lambda x: x['Path'])
    
    os.makedirs('argus/out', exist_ok=True)
    with open('argus/out/endpoints.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Method', 'Path', 'Auth Needed?', 'Takes URL/Param?', 'Returns User Data?'])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated argus/out/endpoints.csv with {len(rows)} endpoints.")

if __name__ == '__main__':
    generate_endpoints()
