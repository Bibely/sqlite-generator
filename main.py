import sqlite3
import os
import re

def create_simple_bible_database(file_path):
    # 파일명에서 버전 코드 추출
    file_name = os.path.basename(file_path)
    version_code = file_name.split('.')[0].upper()  # 예: 'KRV.txt' → 'KRV'
    db_name = f"{version_code}.db"

    # 기존에 동일한 DB 파일이 있으면 삭제
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 스키마 생성 (버전 테이블 삭제, 단순화)
    cursor.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        chapter INTEGER NOT NULL,
        verse INTEGER NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    """)
    conn.commit()

    # 한글 책 이름 매핑
    book_mapping = {
        '창': 'Genesis', '출': 'Exodus', '레': 'Leviticus', '민': 'Numbers', '신': 'Deuteronomy',
        '수': 'Joshua', '삿': 'Judges', '룻': 'Ruth', '삼상': '1 Samuel', '삼하': '2 Samuel',
        '왕상': '1 Kings', '왕하': '2 Kings', '대상': '1 Chronicles', '대하': '2 Chronicles',
        '스': 'Ezra', '느': 'Nehemiah', '에': 'Esther', '욥': 'Job', '시': 'Psalms',
        '잠': 'Proverbs', '전': 'Ecclesiastes', '아': 'Song of Songs', '사': 'Isaiah',
        '렘': 'Jeremiah', '애': 'Lamentations', '겔': 'Ezekiel', '단': 'Daniel',
        '호': 'Hosea', '욜': 'Joel', '암': 'Amos', '옵': 'Obadiah', '욘': 'Jonah',
        '미': 'Micah', '나': 'Nahum', '합': 'Habakkuk', '습': 'Zephaniah',
        '학': 'Haggai', '슥': 'Zechariah', '말': 'Malachi',
        '마': 'Matthew', '막': 'Mark', '눅': 'Luke', '요': 'John', '행': 'Acts',
        '롬': 'Romans', '고전': '1 Corinthians', '고후': '2 Corinthians', '갈': 'Galatians',
        '엡': 'Ephesians', '빌': 'Philippians', '골': 'Colossians', '살전': '1 Thessalonians',
        '살후': '2 Thessalonians', '딤전': '1 Timothy', '딤후': '2 Timothy', '딛': 'Titus',
        '몬': 'Philemon', '히': 'Hebrews', '약': 'James', '벧전': '1 Peter', '벧후': '2 Peter',
        '요일': '1 John', '요이': '2 John', '요삼': '3 John', '유': 'Jude', '계': 'Revelation'
    }

    # 파일 읽고 파싱
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    book_ids = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r'^([가-힣]+)(\d+):(\d+)\s+(.+)', line)
        if match:
            book_kor, chapter, verse, text = match.groups()
            chapter = int(chapter)
            verse = int(verse)

            book_eng = book_mapping.get(book_kor)
            if not book_eng:
                print(f"⚠️ 책 이름 매칭 실패: {book_kor} (파일: {file_name})")
                continue

            # 책(book) 등록 (처음 발견했을 때만)
            if book_eng not in book_ids:
                cursor.execute("INSERT INTO books (name) VALUES (?)", (book_eng,))
                book_ids[book_eng] = cursor.lastrowid

            book_id = book_ids[book_eng]

            # 절(verse) 삽입
            cursor.execute("INSERT INTO verses (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
                           (book_id, chapter, verse, text))

            print(f"✅ {book_id}, {chapter}, {verse} 저장됨")
        else:
            print(f"⚠️ 파싱 실패: {line} (파일: {file_name})")

    conn.commit()
    conn.close()

    print(f"✅ {db_name} 생성 완료!")

def batch_process(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    for file in files:
        file_path = os.path.join(folder_path, file)
        create_simple_bible_database(file_path)

    print("🎉 전체 변환 완료!")

# 실행
batch_process('Data')