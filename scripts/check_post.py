#!/usr/bin/env python3
"""Rà soát nhanh một bài Facebook của Vibe AI Labs trước khi giao.

Script chỉ đưa ra CẢNH BÁO để người viết xem lại. Nó không thay thế phán đoán:
một cảnh báo có thể hợp lệ (ví dụ số liệu do người dùng cung cấp kèm nguồn).

Cách dùng:
    python3 check_post.py bai_viet.txt [--type content|service] [--target-words 300]
    pbpaste | python3 check_post.py [--type content|service]

Khi sửa thông tin liên hệ chính thức, cập nhật đồng thời:
references/brand-foundation.md (mục 10, nguồn chuẩn), SKILL.md và danh sách dưới đây.
"""
import argparse
import re
import sys
import unicodedata

ALLOWED_URLS = [
    "facebook.com/vibe.ai.labs",
    "facebook.com/vibeailabs.ai.vietnam",
    "facebook.com/groups/ai.agents.marketing",
    "facebook.com/groups/vertical.ai.vietnam",
    "facebook.com/groups/chatgptads.vietnamgroup",
    "facebook.com/groups/openclaw.vietnamcommunity",
]
ALLOWED_EMAILS = {"vibeailabs@gmail.com"}
ALLOWED_DOMAINS = ("facebook.com", "gmail.com")

# Số liệu / cụm từ đã xác nhận trong brand-foundation.md — không cảnh báo lại.
APPROVED_NUMBER_PATTERNS = [
    r"30\s*ngày(?:\s*hỗ trợ)?(?:\s*sau\s*bàn\s*giao)?",
    r"(?:trong\s*)?24\s*giờ(?:\s*làm\s*việc)?",
    r"8\s*bước",
    r"19\s*(?:nhóm\s*)?(?:dịch\s*vụ|nhóm)",
    r"10\s*nhóm",
    r"[45]\s*nhóm",
    r"6\s*(?:điểm\s*khác\s*biệt|giá\s*trị)",
    r"9\s*nguyên\s*tắc",
    r"7\s*hình\s*thức",
    r"4\s*cộng\s*đồng",
    r"3\s*năng\s*lực",
    r"(?:năm\s*)?2026",
    r"09:00\s*[–-]\s*18:00",
    r"T2\s*[–-]\s*T6",
]

CHECKS = [
    ("Khẩn cấp giả / ưu đãi chưa xác nhận",
     r"chỉ còn|suất cuối|\d+\s*suất|kết thúc hôm nay|duy nhất hôm nay|early[ -]?bird|ưu đãi|giảm giá|khuyến mãi|miễn phí|nhanh tay|trước ngày \d"),
    ("Tự khen / cam kết quá mức",
     r"hàng đầu|số\s*1\b|tốt nhất|tiên tiến nhất|chuyên nghiệp nhất|uy tín nhất|đảm bảo|cam kết|100\s*%|tuyệt đối|chắc chắn tăng|không bao giờ sai|hoàn toàn chính xác"),
    ("Khai thác nỗi sợ AI thay thế",
     r"thay thế (bạn|toàn bộ|hoàn toàn)|bị AI thay thế|đào thải|mất việc"),
    ("Mở bài sáo rỗng",
     r"trong thời đại (công nghệ|số|4\.0|AI)|AI đang thay đổi thế giới|công nghệ phát triển mạnh mẽ|cách mạng (công nghiệp )?4\.0"),
    ("Có thể ngụ ý quan hệ đối tác",
     r"đối tác (chính thức|của)|partner (chính thức|của)|được (OpenAI|Google|Meta) chứng nhận"),
    ("Tên thương hiệu trong bài mẫu (không phải của Vibe AI Labs)",
     r"Tomorrow Marketers|ACCESSTRADE|C\.P\. Việt Nam|Michelob|Advertising Vietnam|Case Mastery|Growth Max"),
    ("Kênh liên hệ chưa xác nhận",
     r"hotline|\bzalo\s*:|whatsapp|(?:\+84|\b0)\d{2,3}[\s.\-]?\d{3}[\s.\-]?\d{3,4}\b"),
    ("Lời dẫn thừa trước bài",
     r"^\s*(dưới đây là|sau đây là|đây là bài viết)"),
    ("Markdown không hiển thị trên Facebook",
     r"\*\*[^*]+\*\*|^#{1,6}\s|\[[^\]]+\]\(https?://"),
]

NUMBER_CLAIM = re.compile(
    r"(\d+[.,]?\d*\s*(%|phần trăm|lần|giờ|triệu|tỷ|khách hàng|doanh nghiệp|dự án|đơn hàng|lead))",
    re.IGNORECASE,
)
# Số liệu viết bằng chữ / ký hiệu nhân — dạng bịa số hay gặp trong tiếng Việt.
WORD_NUMBER_CLAIM = re.compile(
    r"(gấp\s*(?:đôi|ba|bốn|năm|sáu|bảy|tám|chín|mười|\d+)"
    r"|\bx\s?\d+\b"
    r"|tăng\s+gấp|giảm\s+gấp"
    r"|(?:tăng|giảm|tiết kiệm|tăng trưởng|thiệt hại)[^.\n]{0,30}?(?:một nửa|một phần ba|một phần tư|gấp|hàng (?:chục|trăm|nghìn|triệu))"
    r"|hàng\s+(?:chục|trăm|nghìn|triệu)\s+(?:khách|đơn|lead|người|giờ))",
    re.IGNORECASE,
)
BARE_DOMAIN = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com\.vn|com|vn|dev|io|ai|net|org|co)\b", re.IGNORECASE)


def is_math_alnum(ch):
    return 0x1D400 <= ord(ch) <= 0x1D7FF


def is_emoji(ch):
    return unicodedata.category(ch) == "So" or 0x1F000 <= ord(ch) <= 0x1FAFF


def strip_approved_numbers(text):
    cleaned = text
    for pattern in APPROVED_NUMBER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def main():
    parser = argparse.ArgumentParser(description="Rà soát bài Facebook Vibe AI Labs (chỉ cảnh báo).")
    parser.add_argument("file", nargs="?", help="File bài viết; bỏ trống thì đọc từ stdin.")
    parser.add_argument("--type", choices=["content", "service"], dest="post_type",
                        help="Loại bài để kiểm tra thêm cấu trúc thương hiệu tương ứng.")
    parser.add_argument("--target-words", type=int,
                        help="Độ dài người dùng yêu cầu (số chữ) để đối chiếu, lệch >30%% sẽ cảnh báo.")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"Không đọc được file '{args.file}': {exc.strerror or exc}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("Bài trống, không có gì để kiểm tra.", file=sys.stderr)
        return 2

    warnings = []

    for label, pattern in CHECKS:
        hits = {m.group(0).strip() for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)}
        if hits:
            warnings.append((label, sorted(hits)))

    cleaned = strip_approved_numbers(text)
    nums = sorted({m.group(1).strip() for m in NUMBER_CLAIM.finditer(cleaned)})
    if nums:
        warnings.append(("Số liệu cần có nguồn / do người dùng cung cấp", nums))
    word_nums = sorted({m.group(0).strip() for m in WORD_NUMBER_CLAIM.finditer(text)})
    if word_nums:
        warnings.append(("Số liệu viết bằng chữ cần có nguồn / do người dùng cung cấp", word_nums))

    for url in re.findall(r"https?://\S+|www\.\S+", text):
        if not any(a in url for a in ALLOWED_URLS):
            warnings.append(("URL ngoài danh sách đã xác nhận (chỉ ổn nếu người dùng cung cấp)", [url]))
        if re.search(r"fbclid|utm_", url):
            warnings.append(("Link có tham số tracking dài", [url[:80]]))
    seen_domains = set()
    for match in BARE_DOMAIN.finditer(text):
        domain = match.group(0).lower()
        if domain in seen_domains or any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS):
            continue
        if f"https://{domain}" in text or f"http://{domain}" in text:
            continue  # đã cảnh báo ở phần URL đầy đủ
        seen_domains.add(domain)
        warnings.append(("Domain ngoài danh sách đã xác nhận (chỉ ổn nếu người dùng cung cấp / yêu cầu)", [domain]))

    for email in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)):
        if email.lower() not in ALLOWED_EMAILS and "WORC@Q2" not in email:
            warnings.append(("Email chưa xác nhận", [email]))

    if any(is_math_alnum(c) for c in text):
        warnings.append(("Chữ Unicode in đậm giả (𝐀𝐁𝐂)", ["thay bằng chữ thường"]))

    repeated = re.findall(r"([^\w\s])\1{1,}", text)
    repeated = sorted({r for r in repeated if is_emoji(r)})
    if repeated:
        warnings.append(("Emoji lặp liền nhau", repeated))

    if re.search(r"^[\-—_=]{6,}\s*$", text, re.MULTILINE):
        warnings.append(("Đường phân cách dài", ["bỏ nếu không có mục đích"]))

    hashtags = re.findall(r"(?<!\w)#\w+", text)
    if hashtags:
        warnings.append(("Có hashtag (chỉ giữ nếu phù hợp / được yêu cầu)", hashtags))

    lines = [l for l in text.splitlines() if l.strip()]
    caps = [l for l in lines if len(l) > 15 and l.upper() == l and any(c.isalpha() for c in l)]
    if len(caps) > 2:
        warnings.append(("Quá nhiều dòng viết HOA", [c[:50] for c in caps]))

    long_paras = [p.strip()[:60] + "…" for p in re.split(r"\n\s*\n", text) if len(p.split()) > 90]
    if long_paras:
        warnings.append(("Đoạn quá dài cho Facebook (>90 chữ)", long_paras))

    brand_mentions = len(re.findall(r"vibe ai labs", text, re.IGNORECASE))
    if brand_mentions == 0:
        warnings.append(("Không nhắc tới Vibe AI Labs", ["thêm điểm kết nối thương hiệu"]))

    if args.post_type == "service":
        first_line = lines[0] if lines else ""
        if not ("dịch vụ" in first_line.lower() and "vibe ai labs" in first_line.lower()):
            warnings.append(("Tiêu đề Loại 2 chưa đúng dạng 'DỊCH VỤ ... CỦA VIBE AI LABS: ...'", [first_line[:60]]))
        if 0 < brand_mentions < 3:
            warnings.append((f"Bài dịch vụ mới nhắc Vibe AI Labs {brand_mentions} lần (nên ≥3: tiêu đề, phần giải pháp, CTA)", []))
    if args.post_type == "content" and "góc nhìn từ vibe ai labs" not in text.lower():
        warnings.append(("Bài nội dung chưa có điểm kết nối 'Góc nhìn từ Vibe AI Labs' (nên có, trừ khi người dùng yêu cầu khác)", []))

    if lines and len(lines[0]) > 140:
        warnings.append(("Dòng đầu quá dài, dễ bị Facebook thu gọn trước khi chạm hook", [f"{len(lines[0])} ký tự"]))

    team_hits = re.findall(r"\bteam\b", text, re.IGNORECASE)
    if team_hits:
        warnings.append(("Dùng 'team' thay vì gọi người đọc là 'bạn'", [f"{len(team_hits)} lần"]))

    emoji_count = sum(1 for c in text if is_emoji(c))
    words = len(text.split())
    if args.target_words:
        if abs(words - args.target_words) > 0.3 * args.target_words:
            warnings.append((f"Độ dài lệch yêu cầu ({words} so với ~{args.target_words} chữ)", ["rút gọn / mở rộng lại"]))

    print(f"Độ dài: {words} chữ · {len(lines)} dòng có nội dung · {emoji_count} emoji · nhắc Vibe AI Labs {brand_mentions} lần")
    if not warnings:
        print("Không có cảnh báo.")
        return 0
    print(f"{len(warnings)} cảnh báo cần xem lại:")
    for label, items in warnings:
        print(f"  - {label}: {', '.join(items)}" if items else f"  - {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
