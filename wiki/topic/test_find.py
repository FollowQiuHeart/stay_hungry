'''
题目要求：输入  [
                {id:1, parent_id:0},
	            {id:2, parent_id:1},
                {id:3, parent_id:0},
                {id:4, parent_id:3},
                {id:5, parent_id:1}
                           ]
输出结果：
	    [
	        {id:1, children:[{id:2}...]},
	        {id:3, children:[{id:4}...]}
        ]
'''
def find_father(input_list):
    home = {}
    parent_list = []
    for data in input_list:
        if data['parent_id'] == 0:
            #爹
            parent_list.append({'id':data['id']})
        else:
            #孩子们
            p_id = data['parent_id']
            if p_id not in home:
                home[p_id] = []
                home[p_id].append({'id':data['id']})
            else:
                home[p_id].append({'id': data['id']})

            # home.setdefault(p_id, [])
            # home[p_id].append({'id': data['id']})



    for f in parent_list:
        if f['id'] in home:
            f['children'] = home[f['id']]

    return parent_list

   #  input_list : [{id: 1, parent_id: 0}, {id:2, parent_id: 1}, {id:8, parent_id: 1}]
   # home: { 1 : [{id:'2'},{id:'8'}]}
   # parent_list: [{id:1},{id:3}]
   # parent_list [{id:1, children:[{id:2},{id:8}]}]
input_list = [
    {"id":1, "parent_id":0},
    {"id":2, "parent_id":1},
    {"id":3, "parent_id":0},
    {"id":4, "parent_id":3},
    {"id":5, "parent_id":1}
           ]

print(find_father(input_list))





