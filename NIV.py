import sqlite3
import os
import re

def create_niv_database(file_path, output_path="output/NIV.db"):
    # 1) output 디렉토리 보장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)

    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()

    # 2) 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT NOT NULL,
        chapter INTEGER NOT NULL,
        verse INTEGER NOT NULL,
        text TEXT NOT NULL
    )
    """)
    conn.commit()

    # 3) 정규식 미리 컴파일
    header_re = re.compile(r'^\[(.+)\]$')
    verse_re  = re.compile(r'^(\d+)\.\s*(.+)$')

    current_book    = None
    current_chapter = None
    current_verse   = None
    current_text    = ""

    with open(file_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # 3-1) [책이름 장번호] 헤더
            m_hdr = header_re.match(line)
            if m_hdr:
                # 이전 절이 남아 있으면 저장
                if current_verse is not None:
                    cursor.execute(
                        "INSERT INTO verses (book, chapter, verse, text) VALUES (?, ?, ?, ?)",
                        (current_book, current_chapter, current_verse, current_text.strip())
                    )
                # 새 헤더 파싱
                payload = m_hdr.group(1).rsplit(" ", 1)
                if len(payload) != 2:
                    print(f"⚠️ 헤더 파싱 실패: {line}")
                    current_book = None
                else:
                    current_book, chap = payload
                    try:
                        current_chapter = int(chap)
                    except ValueError:
                        print(f"⚠️ 장 번호 변환 실패: {chap}")
                        current_book = None
                # 절 초기화
                current_verse = None
                current_text = ""
                continue

            # 3-2) 아직 헤더를 못 만났으면 스킵
            if current_book is None:
                continue

            # 3-3) 절 라인: “번호. 본문”
            m_verse = verse_re.match(line)
            if m_verse:
                # 앞의 절 저장
                if current_verse is not None:
                    cursor.execute(
                        "INSERT INTO verses (book, chapter, verse, text) VALUES (?, ?, ?, ?)",
                        (current_book, current_chapter, current_verse, current_text.strip())
                    )
                current_verse = int(m_verse.group(1))
                current_text  = m_verse.group(2).strip()
            else:
                # 절 번호 없는 이어쓰기
                if current_verse is None:
                    print(f"⚠️ 파싱 실패(절 번호 없음): {line}")
                else:
                    current_text += " " + line

    # 4) 마지막 절 저장
    if current_verse is not None:
        cursor.execute(
            "INSERT INTO verses (book, chapter, verse, text) VALUES (?, ?, ?, ?)",
            (current_book, current_chapter, current_verse, current_text.strip())
        )

    conn.commit()
    conn.close()
    print(f"✅ 데이터베이스 생성 완료: {output_path}")

if __name__ == "__main__":
    create_niv_database('data/NIV.txt')