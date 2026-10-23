#!/usr/bin/env python3
"""Rà soát nhanh một bài Facebook của Vibe AI Labs trước khi giao.

Script chỉ đưa ra CẢNH BÁO để người viết xem lại. Nó không thay thế phán đoán:
một cảnh báo có thể hợp lệ (ví dụ số liệu do người dùng cung cấp kèm nguồn).

Cách dùng:
    python check_post.py bai_viet.txt
    pbpaste | python check_post.py
"""
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
    r"(\d+[.,]?\d*\s*(%|phần trăm|lần|giờ|triệu|tỷ|khách hàng|doanh nghiệp|dự án))",
    re.IGNORECASE,
)


def is_math_alnum(ch):
    return 0x1D400 <= ord(ch) <= 0x1D7FF


def is_emoji(ch):
    return unicodedata.category(ch) == "So" or 0x1F000 <= ord(ch) <= 0x1FAFF


def main():
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    warnings = []

    for label, pattern in CHECKS:
        hits = {m.group(0).strip() for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)}
        if hits:
            warnings.append((label, sorted(hits)))

    nums = sorted({m.group(1).strip() for m in NUMBER_CLAIM.finditer(text)})
    if nums:
        warnings.append(("Số liệu cần có nguồn / do người dùng cung cấp", nums))

    for url in re.findall(r"https?://\S+|www\.\S+", text):
        if not any(a in url for a in ALLOWED_URLS):
            warnings.append(("URL ngoài danh sách đã xác nhận (chỉ ổn nếu người dùng cung cấp)", [url]))
        if re.search(r"fbclid|utm_", url):
            warnings.append(("Link có tham số tracking dài", [url[:80]]))

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

    if "vibe ai labs" not in text.lower():
        warnings.append(("Không nhắc tới Vibe AI Labs", ["thêm điểm kết nối thương hiệu"]))

    team_hits = re.findall(r"\bteam\b", text, re.IGNORECASE)
    if team_hits:
        warnings.append(("Dùng 'team' thay vì gọi người đọc là 'bạn'", [f"{len(team_hits)} lần"]))

    emoji_count = sum(1 for c in text if is_emoji(c))
    words = len(text.split())

    print(f"Độ dài: {words} chữ · {len(lines)} dòng có nội dung · {emoji_count} emoji")
    if not warnings:
        print("Không có cảnh báo.")
        return
    print(f"{len(warnings)} cảnh báo cần xem lại:")
    for label, items in warnings:
        print(f"  - {label}: {', '.join(items)}")


if __name__ == "__main__":
    main()
