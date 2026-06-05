# PickEat Django Backend

## 프로젝트 구조
```
pickeat/
├── pickeat/          # 프로젝트 설정
│   ├── settings.py
│   └── urls.py
├── accounts/         # 회원가입/로그인
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── restaurants/      # 식당 추천/저장
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── management/commands/import_restaurants.py
├── restaurants.csv   # 식당 데이터
└── db.sqlite3
```

## 초기 설정

### 1. 패키지 설치
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers anthropic
```

### 2. 환경변수 설정
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. DB 마이그레이션
```bash
python manage.py migrate
```

### 4. 식당 데이터 import
```bash
python manage.py import_restaurants restaurants.csv
```

### 5. 서버 실행
```bash
python manage.py runserver
```

---

## API 명세

### 인증 (accounts)

#### 회원가입
```
POST /api/auth/register/
Content-Type: application/json

{
  "username": "sunny123",
  "nickname": "맛집탐험가",
  "password": "mypassword"
}
```
→ 응답: `{ user, access, refresh }`

#### 로그인
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "sunny123",
  "password": "mypassword"
}
```
→ 응답: `{ user, access, refresh }`

#### 내 정보 조회
```
GET /api/auth/me/
Authorization: Bearer <access_token>
```

#### 닉네임 변경
```
PATCH /api/auth/me/nickname/
Authorization: Bearer <access_token>

{ "nickname": "새닉네임" }
```

#### 토큰 갱신
```
POST /api/auth/token/refresh/
{ "refresh": "<refresh_token>" }
```

---

### 식당 (restaurants)

#### AI 추천 받기
```
POST /api/restaurants/recommend/
Authorization: Bearer <access_token>

{
  "food_types": ["한식", "일식"],
  "moods": ["데이트", "혼밥"],
  "distance": "도보 5분",
  "meal_count": "혼밥"
}
```
→ 응답:
```json
{
  "recommendations": [
    {
      "rank": 1,
      "id": 5,
      "naver_id": "1234567",
      "name": "한성 닭한마리",
      "picture": "https://...",
      "is_saved": false,
      "reason": "데이트하기 좋은 분위기의 한식당"
    },
    ...
  ]
}
```

#### 식당 상세 조회
```
GET /api/restaurants/<id>/
Authorization: Bearer <access_token>
```

#### 식당 저장
```
POST /api/restaurants/<id>/save/
Authorization: Bearer <access_token>
```

#### 저장 취소
```
DELETE /api/restaurants/<id>/save/
Authorization: Bearer <access_token>
```

#### MY PICKS (저장 목록)
```
GET /api/restaurants/my-picks/
Authorization: Bearer <access_token>
```
→ 응답:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "restaurant": { "id": 5, "name": "...", "picture": "...", "is_saved": true },
      "saved_at": "2026-06-06T12:00:00"
    }
  ]
}
```

---

## 프론트엔드 연동 참고

### JWT 토큰 관리
```js
// 로그인 후 localStorage에 저장
localStorage.setItem('access_token', response.access)
localStorage.setItem('refresh_token', response.refresh)

// API 요청 시 헤더 추가
headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
```

### 홈 화면 옵션 매핑 (Figma 기준)
```js
// 음식 종류
const foodTypes = ['한식', '양식', '일식', '중식', '분식', '카페/디저트', '아무거나']

// 분위기
const moods = ['조용한', '힘찬', '데이트', '가성비', '리뷰 좋은', '사진 맛집']

// 거리
const distances = ['도보 5분', '10분', '15분', '상관없음']

// 식사 상황
const mealCounts = ['혼밥', '같이']
```
