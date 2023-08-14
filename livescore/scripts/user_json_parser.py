import json

dict_list = []
with open('livescore/data/2324/user_db.dat') as file:
    users = file.readlines()
    print(users)
    for user in users:
        user_list = user.split('\t')
        print(user)
        dict_entry = {
            'model': 'livescore.User',
            'pk': user_list[1],
            'fields': {
                'name': user_list[0],
                'email': user_list[2]
                }
            }
        dict_list.append(dict_entry)


with open('livescore/data/2324/users.json', 'w') as file:
    file.write(json.dumps(dict_list))
