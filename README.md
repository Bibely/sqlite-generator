# 📖 Bible SQLite Database Generator

**Bible SQLite Database Generator**는 다양한 성경 버전의 텍스트 파일(`.txt`)을  
**SQLite3 데이터베이스 파일(.db)** 로 변환하는 Python 기반 프로젝트입니다.

텍스트 파일당 하나의 SQLite DB 파일을 생성하여,  
성경 앱, 웹 서비스 등에서 효율적으로 사용할 수 있도록 지원합니다.

---

## ✨ Features

- **자동 변환** : `Data/` 폴더 내 모든 `.txt` 파일을 순회하며 SQLite 파일 생성
- **가벼운 스키마** : books, verses 테이블만 생성하여 간결하고 빠른 접근 지원
- **파일명 기반 버전 관리** : `KRV.txt`, `NIV.txt` 등 파일명으로 버전 식별
- **한글 성경 약어 자동 매칭** : 창(Genesis), 출(Exodus) 등 매핑
- **실시간 파싱 오류 로그 출력** : 문제 발생 시 즉시 확인 가능

---

## 🗂 폴더 구조
```
├── Data/
│   ├── KRV.txt
│   ├── NIV.txt
│   └── …
├── bible_generator.py
└── README.md
```

---

## 🔍 SQLite 스키마 구조

```sql
CREATE TABLE books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE verses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  text TEXT NOT NULL,
  FOREIGN KEY (book_id) REFERENCES books(id)
);
```

---

## 📄 License

MIT License.

(단, 성경 본문 텍스트 파일은 각 번역본의 저작권 정책을 준수해야 합니다.)