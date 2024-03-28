import os
import re
import csv

output = {}
ip_pattern = r'([\d]+\.[\d]+\.[\d]+\.[\d]+|\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b)'

def remove_duplicates(cleaned_lines):
    ip_count = 0
    filtered_list = []
    
    for item in cleaned_lines:
        if re.match(ip_pattern, item):
            ip_count += 1
        if ip_count <= 1:
            filtered_list.append(item)    
    return filtered_list

def calculate_average_time(cleaned_lines):
    total_time = 0
    count = 0
    for item in cleaned_lines[3:]:
        total_time += float(item)
        count += 1
    return round(total_time / count, 2)

def process_line(line, hop):
    cleaned_lines = line.split(' ')
    cleaned_lines = [item for item in cleaned_lines if item != 'ms'] # remove ms
    cleaned_lines = [item for item in cleaned_lines if '*' not in item] # remove *
    cleaned_lines = list(filter(None, cleaned_lines)) # remove empty strings
    cleaned_lines = remove_duplicates(cleaned_lines)
            
    hop_dict = {}
    hop_dict['hop'] = cleaned_lines[0]
    hop_dict['address'] = cleaned_lines[1]
    hop_dict['ip'] = re.sub(r'[()]', '', cleaned_lines[2])
    hop_dict['average_time'] = calculate_average_time(cleaned_lines)
    
    return hop_dict

def process_log_contents(contents):
    hops = {'www.harvard.edu': [], 'www.cuhk.edu.hk': [], 'www.unimelb.edu.au': [], 'www5.usp.br': []}
    current_hop = None
    
    for line in contents.split('\n'):
        match = re.search(ip_pattern, line)
        if match:
            hop = match.group(0)
            
            if 'traceroute' in line:
                current_hop = str(hop)
            else:
                hop_dict = process_line(line, hop)
                
                hops[current_hop].append(hop_dict)
    return hops

def loop_through_files(folder='TraceRouteLogs'):
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), 'r') as f:
                contents = f.read()
                hops = process_log_contents(contents)
                output[file] = hops

def save_to_csv(output):
    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['File', 'Address', 'Hop', 'IP', 'Average Time'])
        for file, hops in output.items():
            for address, hop_list in hops.items():
                for hop in hop_list:
                    writer.writerow([file, address, hop['hop'], hop['ip'], hop['average_time']])
                    

if __name__ == '__main__':
    loop_through_files()
    save_to_csv(output)
    
    # Print out neatly with labels
    # for file, hops in output.items():
    #     print(f'File: {file}')
    #     for address, hop_list in hops.items():
    #         print(f'\tAddress: {address}')
    #         for hop in hop_list:
    #             print(f'\t\tHop: {hop["hop"]}, Address: {hop["address"]}, IP: {hop["ip"]}, Average Time: {hop["average_time"]}')
    #         print()
            
'''
    output format
    output = {
        'file1.txt': {
            'www.harvard.edu': [
                {
                    'hop': 1,
                    'address': 'www.com',
                    'ip': '0.0.0.0',
                    'average_time': 0.0
            }
        ]
    }
'''

'''
    csv format
    File, Address, Hop, IP, Average Time   
    file1.txt, www.harvard.edu, 1, 0.0.0.0, 0.0
'''