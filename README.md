# 💊 DrugTime

> **Medication Reminder, Drug-Interaction Safety, and AI-Assisted Care Platform**

DrugTime là nền tảng quản lý thuốc di động dành cho bệnh nhân Việt Nam, giúp nhắc uống thuốc đúng giờ, cảnh báo tương tác thuốc-thuốc/thuốc-thực phẩm theo danh mục dược phẩm Việt Nam, và hỗ trợ người thân giám sát tuân thủ điều trị từ xa.

[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Tính năng chính](#-tính-năng-chính)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Tech Stack](#-tech-stack)
- [Cài đặt & Chạy](#-cài-đặt--chạy)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Quy trình phát triển](#-quy-trình-phát-triển)
- [Đội ngũ](#-đội-ngũ)
- [Tài liệu tham khảo](#-tài-liệu-tham-khảo)
- [License](#-license)

---

## 🎯 Tổng quan

### Vấn đề

Khảo sát 60 người tại Đà Nẵng cho thấy **75% quên uống thuốc** ít nhất 1 lần trong tuần qua, trong khi chỉ **5%** sử dụng ứng dụng nhắc thuốc. Các ứng dụng quốc tế hiện tại (Medisafe, MyTherapy) không hỗ trợ danh mục dược phẩm Việt Nam hay kiểm tra tương tác thuốc theo QĐ 5948/QĐ-BYT.

### Giải pháp

DrugTime cung cấp một nền tảng tập trung cho:
- Quản lý thuốc & lịch uống thuốc
- Nhắc nhở uống thuốc qua thông báo đẩy
- Cảnh báo tương tác thuốc-thuốc, thuốc-thực phẩm từ nguồn dữ liệu chính thống Việt Nam
- Liên kết người thân để giám sát tuân thủ từ xa
- Gợi ý bữa ăn phù hợp bằng AI

> ⚠️ **Disclaimer**: DrugTime là hệ thống hỗ trợ quản lý thuốc và cung cấp thông tin tham khảo. Ứng dụng **không thay thế** bác sĩ hoặc dược sĩ trong việc ra quyết định lâm sàng.

---

## ✨ Tính năng chính

### 👤 Bệnh nhân (Patient)

| Nhóm tính năng | Mô tả |
|---|---|
| **Quản lý tài khoản & Đồng ý** | Đăng ký/Đăng nhập, đồng ý mục đích xử lý dữ liệu riêng biệt (PDPL 2025), thu hồi đồng ý, yêu cầu xóa dữ liệu |
| **Quản lý thuốc** | Thêm thuốc thủ công hoặc quét vỉ thuốc (on-device OCR), xác nhận thông tin thuốc, quản lý lịch uống |
| **Nhắc nhở & Tuân thủ** | Nhận thông báo nhắc uống thuốc, xác nhận đã uống, xem lịch sử tuân thủ |
| **Tra cứu an toàn thuốc** | Tra cứu thông tin thuốc, cảnh báo tương tác thuốc-thuốc & thuốc-thực phẩm |
| **Liên kết gia đình** | Liên kết tài khoản người thân qua QR/mã giới thiệu, quản lý quyền chia sẻ dữ liệu |
| **Trợ lý AI** | Gợi ý bữa ăn phù hợp với thuốc đang dùng (kèm giải thích) |
| **Chế độ Đơn giản** | Giao diện tương phản cao, tối giản cho người dùng lớn tuổi |

### 👨‍👩‍👦 Người thân (Family Member)

- Liên kết tài khoản bệnh nhân
- Nhận cảnh báo bỏ lỡ liều thuốc theo thời gian thực
- Xem lịch sử tuân thủ, tra cứu an toàn thuốc cho người thân
- Quản lý nhiều bệnh nhân liên kết

### 🛡️ Quản trị viên (Admin)

- Quản lý danh mục thuốc & tương tác (CRUD)
- Đồng bộ dữ liệu từ nguồn dược phẩm Việt Nam
- Quản lý tuân thủ PDPL 2025 / Nghị định 356 (DPIA, xử lý xóa dữ liệu, nhật ký truy cập)

---

## 🏗 Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                        External Services                            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ Google ML Kit│  │     FCM      │  │ VN Drug Regulatory Source │  │
│  │ (on-device)  │  │ (push notif) │  │ (DAV, QĐ 5948, Dược thư) │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────────┬─────────────┘  │
│         │                 │                        │                │
└─────────┼─────────────────┼────────────────────────┼────────────────┘
          │                 │                        │
┌─────────▼─────────┐      │      ┌─────────────────▼──────────────┐
│   Flutter Mobile   │      │      │      Admin Web Dashboard       │
│  (Android & iOS)   │      │      │     (React + Next.js)          │
│  Patient & Family  │      │      │        on Vercel               │
└─────────┬──────────┘      │      └──────────────┬────────────────┘
          │                 │                     │
          └────────┬────────┘─────────────────────┘
                   │          HTTPS (Caddy)
          ┌────────▼────────────────────────────────┐
          │          Backend API (FastAPI)           │
          │        Modular Monolith Architecture     │
          │  ┌──────────────────────────────────┐   │
          │  │ medication │ interaction │ reminder│  │
          │  │  partner   │   admin    │ consent │  │
          │  └──────────────────────────────────┘   │
          └────────┬────────────────┬───────────────┘
                   │                │
          ┌────────▼──────┐  ┌─────▼──────────┐
          │  RQ + Redis   │  │    Supabase     │
          │ (Background   │  │  PostgreSQL +   │
          │   Jobs)       │  │  pgvector +     │
          │               │  │  Storage        │
          └───────────────┘  └────────────────┘

          ▲ All deployed on Oracle Cloud "Always Free" VM ▲
```

### Architecture Style

- **Modular Monolith**: Một process duy nhất, chia thành các module độc lập (medication, interaction, reminder, partner, admin), mỗi module sở hữu dữ liệu riêng.
- **Hexagonal (Ports & Adapters)**: Tách biệt business logic khỏi infrastructure trong mỗi module.
- **Sync/Async**: FastAPI cho các thao tác cần tính toàn vẹn dữ liệu ngay lập tức; RQ cho các tác vụ nền (nhắc nhở, đồng bộ danh mục).

---

## 🛠 Tech Stack

| Layer | Công nghệ |
|---|---|
| **Mobile App** | Flutter (Android & iOS) |
| **Admin Dashboard** | React + Next.js (Vercel) |
| **Backend API** | Python + FastAPI |
| **Database & Storage** | Supabase (PostgreSQL + pgvector + Storage) |
| **Background Jobs** | RQ + Redis |
| **Blister-pack Scan** | Google ML Kit (on-device OCR) |
| **Push Notifications** | Firebase Cloud Messaging (FCM) |
| **Deployment** | Oracle Cloud Always Free VM + Caddy (HTTPS) |
| **AI Meal Suggestion** | LLM-based |
| **Version Control** | GitHub |
| **Project Management** | Jira, Slack, Google Drive |

### Nguồn dữ liệu dược phẩm

| Nguồn | Mục đích |
|---|---|
| [dichvucong.dav.gov.vn](https://dichvucong.dav.gov.vn) / [drugbank.vn](https://drugbank.vn) | Danh mục thuốc được cấp phép (Cục Quản lý Dược) |
| [tuongtacthuoc.ehealth.gov.vn](https://tuongtacthuoc.ehealth.gov.vn) | Danh mục tương tác thuốc (QĐ 5948/QĐ-BYT) |
| Dược thư Quốc gia Việt Nam 2022 | Thông tin thuốc & cảnh báo tương tác thuốc-thực phẩm |

---

## 🚀 Cài đặt & Chạy

### Yêu cầu

- Flutter SDK >= 3.x
- Python >= 3.11
- Node.js >= 18
- Redis
- Tài khoản Supabase

### Mobile App (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

### Backend API (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Admin Dashboard (Next.js)

```bash
cd admin
npm install
npm run dev
```

---

## 📁 Cấu trúc dự án

```
DrugTime/
├── .github/
│   └── workflows/
│       └── mobile-ci.yml          # CI pipeline cho mobile app
├── mobile/                        # Flutter app (Patient & Family Member)
│   ├── lib/
│   ├── android/
│   ├── ios/
│   └── pubspec.yaml
├── backend/                       # Python FastAPI backend
│   ├── modules/
│   │   ├── medication/
│   │   ├── interaction/
│   │   ├── reminder/
│   │   ├── partner/
│   │   ├── admin/
│   │   └── consent/
│   ├── main.py
│   └── requirements.txt
├── admin/                         # React + Next.js admin dashboard
│   ├── src/
│   └── package.json
├── docs/                          # Tài liệu dự án
│   ├── DrugTime_SRS.docx
│   ├── Proposal.docx
│   └── Diagram.drawio
└── README.md
```

---

## 📅 Quy trình phát triển

**Methodology**: Scrum (6 sprints × 2 tuần)

| Sprint | Thời gian | Nội dung |
|---|---|---|
| **Sprint 1** | 14/09 – 27/09 | Platform setup, Auth, Consent flows, Drug-data sync, DPIA draft |
| **Sprint 2** | 28/09 – 11/10 | Medication CRUD, Local notifications, Dose confirmation, Admin dashboard |
| **Sprint 3** | 12/10 – 25/10 | Adherence history, Family linking (QR/referral), Missed-dose alerts |
| **Sprint 4** | 26/10 – 08/11 | Medication look-up, Drug interaction checks, Cross-device testing |
| **Sprint 5** | 09/11 – 22/11 | Blister-pack scan (OCR), Simple Mode UI, Consent withdrawal flow |
| **Sprint 6** | 23/11 – 06/12 | AI meal suggestion, DPIA finalized, Full regression testing |

### Branching Strategy

```
main
├── develop
│   ├── feature/auth
│   ├── feature/medication
│   ├── feature/reminder
│   ├── feature/interaction
│   ├── feature/family-link
│   └── feature/ai-meal
├── hotfix/*
└── release/*
```

---

## 👥 Đội ngũ

**Team C1SE.07** — International School, Duy Tan University

| Thành viên | MSSV | Vai trò |
|---|---|---|
| Nguyễn Ngọc Phúc | 29219051745 | Team Leader / Scrum Master, Dev, QA |
| Nguyễn Quang Bảo | 29211158850 | Dev, QA, DevOps |
| Nguyễn Tấn Đức | 29211156669 | Dev, QA, DevOps |
| Nguyễn Văn Nguyên | 29211364802 | BA, Dev, QA |
| Đặng Ngô Ngọc Việt | 29219064788 | Dev, QA, DevOps |

**Mentor**: B.Eng. Nguyễn Trọng Giáp — Kaopiz Da Nang

---

## 📚 Tài liệu tham khảo

1. Dược thư Quốc gia Việt Nam, tập 1 & 2, 2022
2. Bộ Y tế, QĐ 5948/QĐ-BYT — Danh mục tương tác thuốc chống chỉ định
3. Luật Bảo vệ dữ liệu cá nhân 2025 & Nghị định 356/2025/NĐ-CP
4. Cục Quản lý Dược — Danh mục thuốc lưu hành
5. [Flutter Documentation](https://docs.flutter.dev/)
6. [FastAPI Documentation](https://fastapi.tiangolo.com/)
7. [Supabase Documentation](https://supabase.com/docs)

---

## 📄 License

*Capstone Project 1 — Duy Tan University, International School, 2026*

---

<p align="center">
  Made with ❤️ by Team C1SE.07
</p>
