# fb-writing

Skill viết bài Facebook tiếng Việt cho **Vibe AI Labs** (Marketing × AI × Creative), dùng được với Devin, Claude Code và các agent hỗ trợ định dạng `SKILL.md`.

## Cài đặt

```bash
# Theo project
git clone https://github.com/vibeailabs-tech/fb-writing-skill.git .devin/skills/fb-writing

# Hoặc global
git clone https://github.com/vibeailabs-tech/fb-writing-skill.git ~/.config/devin/skills/fb-writing
```

## Cấu trúc

- `SKILL.md`: hướng dẫn chính (kèm thẻ tóm tắt nhanh)
- `references/brand-foundation.md`: định vị thương hiệu, 19 nhóm dịch vụ, triết lý, thông tin liên hệ đã xác nhận
- `references/golden-samples.md`: bài mẫu chuẩn hoàn chỉnh của Vibe AI Labs (1 bài nội dung, 1 bài dịch vụ)
- `references/content-post.md` / `service-post.md`: cấu trúc hai loại bài
- `references/voice-and-format.md`: giọng văn và định dạng Facebook
- `references/style-samples.md`: bài mẫu của thương hiệu khác để học phong cách (không chép nội dung)
- `scripts/check_post.py`: rà lỗi bài viết (lời hứa quá mức, khẩn cấp giả, số liệu bịa kể cả viết bằng chữ, liên hệ chưa xác nhận…). Chạy: `python3 scripts/check_post.py <file> --type content|service`
- `evals/evals.json`: bộ test prompt kèm tiêu chí chấm (assertions)

Liên hệ: vibeailabs@gmail.com
