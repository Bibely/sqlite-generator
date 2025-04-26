import sqlite3
import os
import re

# 한글 책 이름 매핑
chapter_mapping_ko = {
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

# 영어 책 이름 매핑
chapter_mapping_en = {
    'Gen': 'Genesis', 'Exod': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deut': 'Deuteronomy',
    'Josh': 'Joshua', 'Judg': 'Judges', 'Ruth': 'Ruth', '1Sam': '1 Samuel', '2Sam': '2 Samuel',
    '1Kgs': '1 Kings', '2Kgs': '2 Kings', '1Chr': '1 Chronicles', '2Chr': '2 Chronicles',
    'Ezra': 'Ezra', 'Neh': 'Nehemiah', 'Esth': 'Esther', 'Job': 'Job', 'Ps': 'Psalms',
    'Prov': 'Proverbs', 'Eccl': 'Ecclesiastes', 'Song': 'Song of Songs', 'Isa': 'Isaiah',
    'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Ezek': 'Ezekiel', 'Dan': 'Daniel',
    'Hos': 'Hosea', 'Joel': 'Joel', 'Amos': 'Amos', 'Obad': 'Obadiah', 'Jonah': 'Jonah',
    'Mic': 'Micah', 'Nah': 'Nahum', 'Hab': 'Habakkuk', 'Zeph': 'Zephaniah',
    'Hag': 'Haggai', 'Zech': 'Zechariah', 'Mal': 'Malachi',
    'Matt': 'Matthew', 'Mark': 'Mark', 'Luke': 'Luke', 'John': 'John', 'Acts': 'Acts',
    'Rom': 'Romans', '1Cor': '1 Corinthians', '2Cor': '2 Corinthians', 'Gal': 'Galatians',
    'Eph': 'Ephesians', 'Phil': 'Philippians', 'Col': 'Colossians', '1Thess': '1 Thessalonians',
    '2Thess': '2 Thessalonians', '1Tim': '1 Timothy', '2Tim': '2 Timothy', 'Titus': 'Titus',
    'Philem': 'Philemon', 'Heb': 'Hebrews', 'James': 'James', '1Pet': '1 Peter', '2Pet': '2 Peter',
    '1John': '1 John', '2John': '2 John', '3John': '3 John', 'Jude': 'Jude', 'Rev': 'Revelation'
}

def create_bible_database(file_path):
    file_name = os.path.basename(file_path)
    version_code = file_name.split('.')[0].upper()
    db_name = f"output/{version_code}.db"

    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 스키마 생성
    cursor.execute("""
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter INTEGER NOT NULL,
        chapter_name TEXT NOT NULL,
        verse INTEGER NOT NULL,
        text TEXT NOT NULL
    )
    """)
    conn.commit()

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 한글 or 영어 파싱
        match = re.match(r'^([가-힣]+|\w+)\.?(\d+):(\d+)\s+(.+)', line)
        if match:
            book_code = match.group(1)
            chapter = int(match.group(2))
            verse = int(match.group(3))
            text = match.group(4)

            if book_code in chapter_mapping_ko:
                chapter_name = chapter_mapping_ko[book_code]
            elif book_code in chapter_mapping_en:
                chapter_name = chapter_mapping_en[book_code]
            else:
                print(f"⚠️ 책 이름 매칭 실패: {book_code} (파일: {file_name})")
                continue

            # 절 삽입
            cursor.execute(
                "INSERT INTO verses (chapter, chapter_name, verse, text) VALUES (?, ?, ?, ?)",
                (chapter, chapter_name, verse, text)
            )
        else:
            print(f"⚠️ 파싱 실패: {line} (파일: {file_name})")

    conn.commit()
    conn.close()

    print(f"✅ {db_name} 생성 완료!")

def batch_process(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    for file in files:
        file_path = os.path.join(folder_path, file)
        # NIV 버전은 다른 파싱 script를 사용
        if "NIV" in file_path:
            return;

        create_bible_database(file_path)

    print("🎉 전체 변환 완료!")

if __name__ == "__main__":
    batch_process('data')