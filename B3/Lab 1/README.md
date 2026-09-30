## 1. Xác định resources trong miền
- Users
- Posts
- Comments
- Tags
- Profiles
- Followers

## 2. Phân loại collection / item / sub-resource
Loại Resource | Ví Dụ | Mô Tả |
| :--- | :--- | :--- |
| **Collection** | `/posts`, `/users` | Tập các tài nguyên cùng loại |
| **Item** | `/posts/{post_id}`, `/users/{user_id}` | Một đối tượng trong collection|
| **Sub-resource** | `/posts/{post_id}/comments` | Tập tài nguyên con nằm trong tài nguyên cha |

## 2. Vẽ sơ đồ cây endpoint và quyết định version segment
```text
/v1
├── /posts 
│   ├── GET          
│   ├── POST         
│   └── /{post_id} 
│       ├── GET      
│       ├── PUT      
│       ├── DELETE   
│       ├── /comments 
│       │   ├── GET  
│       │   └── POST 
│       └── /tags 
│           ├── GET  
│           └── POST 
├── /comments/{comment_id}
│   ├── PUT          
│   └── DELETE       
├── /users
│   ├── GET          
│   └── /{user_id} 
│       ├── GET      
│       ├── /profile 
│       │   ├── GET  
│       │   └── PUT  
│       ├── /followers
│       │   └── GET  
│       └── /following
│           ├── GET  
│           └── POST 
└── /tags 
    └── GET          