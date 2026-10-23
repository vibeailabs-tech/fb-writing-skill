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

- `SKILL.md`: hướng dẫn chính
- `references/`: định vị thương hiệu, giọng văn, cấu trúc bài nội dung / dịch vụ, bài mẫu
- `scripts/check_post.py`: rà lỗi bài viết (lời hứa quá mức, khẩn cấp giả, liên hệ chưa xác nhận…)
- `evals/evals.json`: bộ test prompt

Liên hệ: vibeailabs@gmail.com
