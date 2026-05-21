"""Mock data source for MVP testing without real external websites."""

import asyncio
import random

from app.spiders.base import BaseSpider, CompanySearchResult, CompanyDetailResult

MOCK_COMPANIES = [
    {
        "name": "北京星辰科技有限公司",
        "credit_code": "91110000MA01ABCDEFG",
        "address": "北京市海淀区中关村大街18号",
        "industry": "科技推广和应用服务业",
        "legal_representative": "张明远",
        "registered_capital": "5000万元人民币",
        "establish_date": "2015-03-12",
        "business_scope": "技术开发、技术咨询、技术服务、技术转让；软件开发；计算机系统服务；销售计算机、软件及辅助设备、电子产品、通讯设备。",
        "status": "存续",
        "phone": "010-88886666",
        "email": "contact@xingchen-tech.com",
        "website": "https://www.xingchen-tech.com",
    },
    {
        "name": "上海云帆网络信息有限公司",
        "credit_code": "91310000MA1FGHIJKL",
        "address": "上海市浦东新区张江高科技园区碧波路690号",
        "industry": "互联网和相关服务",
        "legal_representative": "李晓明",
        "registered_capital": "2000万元人民币",
        "establish_date": "2018-07-20",
        "business_scope": "互联网信息服务；数据处理；软件开发；网络科技领域内的技术开发、技术咨询。",
        "status": "存续",
        "phone": "021-55558888",
        "email": "info@yunfan-net.com",
        "website": "https://www.yunfan-net.com",
    },
    {
        "name": "深圳前海智慧大数据有限公司",
        "credit_code": "91440300MA5MNOPQRS",
        "address": "深圳市南山区科技园南区高新南一道008号",
        "industry": "软件和信息技术服务业",
        "legal_representative": "王建国",
        "registered_capital": "10000万元人民币",
        "establish_date": "2016-11-05",
        "business_scope": "大数据分析服务；人工智能算法研发；云计算服务；数据处理和存储支持服务。",
        "status": "存续",
        "phone": "0755-26888888",
        "email": "bd@qianhui-data.com",
        "website": "https://www.qianhui-data.com",
    },
    {
        "name": "杭州绿源生态农业发展有限公司",
        "credit_code": "91330100MA2TUVWXYZ",
        "address": "杭州市西湖区文三路90号",
        "industry": "农业",
        "legal_representative": "陈志强",
        "registered_capital": "800万元人民币",
        "establish_date": "2019-04-15",
        "business_scope": "生态农业技术开发；农产品种植、销售；农业观光旅游服务；农业技术咨询。",
        "status": "存续",
        "phone": "0571-88889999",
        "email": "contact@lvyuan-agri.com",
        "website": "https://www.lvyuan-agri.com",
    },
    {
        "name": "广州恒达机械制造有限公司",
        "credit_code": "91440100MA5ABCDE01",
        "address": "广州市天河区科韵路16号",
        "industry": "通用设备制造业",
        "legal_representative": "赵德强",
        "registered_capital": "3000万元人民币",
        "establish_date": "2010-08-28",
        "business_scope": "机械设备研发、制造、销售；自动化生产线设计安装；货物进出口贸易。",
        "status": "存续",
        "phone": "020-38886666",
        "email": "sales@hengda-mach.com",
        "website": "https://www.hengda-mach.com",
    },
    {
        "name": "成都天府生物制药有限公司",
        "credit_code": "91510100MA6FGHIJ23",
        "address": "成都市高新区天府大道中段1366号",
        "industry": "医药制造业",
        "legal_representative": "刘慧琳",
        "registered_capital": "8000万元人民币",
        "establish_date": "2017-01-10",
        "business_scope": "生物药品研发、生产、销售；医疗器械技术开发；技术转让、技术服务。",
        "status": "存续",
        "phone": "028-86001234",
        "email": "hr@tianfu-bio.com",
        "website": "https://www.tianfu-bio.com",
    },
    {
        "name": "南京智联教育咨询有限公司",
        "credit_code": "91320100MA1KLMNO45",
        "address": "南京市鼓楼区中山路81号",
        "industry": "教育",
        "legal_representative": "孙文博",
        "registered_capital": "500万元人民币",
        "establish_date": "2020-06-01",
        "business_scope": "教育咨询；企业管理咨询；文化艺术交流活动组织策划；会议及展览服务。",
        "status": "存续",
        "phone": "025-83335555",
        "email": "service@zhilian-edu.com",
        "website": "https://www.zhilian-edu.com",
    },
    {
        "name": "武汉光谷新能源科技有限公司",
        "credit_code": "91420100MA4PQRST67",
        "address": "武汉市东湖新技术开发区光谷大道66号",
        "industry": "电气机械和器材制造业",
        "legal_representative": "黄伟民",
        "registered_capital": "6000万元人民币",
        "establish_date": "2014-09-18",
        "business_scope": "新能源技术研发；太阳能电池组件制造销售；储能系统解决方案；电力工程施工。",
        "status": "存续",
        "phone": "027-87654321",
        "email": "info@guanggu-energy.com",
        "website": "https://www.guanggu-energy.com",
    },
]


class QichachaMockSpider(BaseSpider):
    """Mock spider that returns static sample data. Useful for MVP demos."""

    source_name = "qichacha_mock"

    async def search(self, keyword: str, **filters) -> list[CompanySearchResult]:
        await asyncio.sleep(random.uniform(0.5, 1.5))  # simulate network delay

        keyword_lower = keyword.lower()
        results = []
        for c in MOCK_COMPANIES:
            # Match by name, industry, or address
            if any(keyword_lower in c[field].lower() for field in ("name", "industry", "address")):
                results.append(CompanySearchResult(
                    name=c["name"],
                    credit_code=c["credit_code"],
                    address=c["address"],
                    industry=c["industry"],
                    source=self.source_name,
                    source_url=f"https://mock.example.com/company/{c['credit_code']}",
                ))
        # If no exact match, return all (simulates fuzzy search)
        if not results:
            for c in MOCK_COMPANIES:
                results.append(CompanySearchResult(
                    name=c["name"],
                    credit_code=c["credit_code"],
                    address=c["address"],
                    industry=c["industry"],
                    source=self.source_name,
                    source_url=f"https://mock.example.com/company/{c['credit_code']}",
                ))
        return results

    async def get_detail(self, company: CompanySearchResult) -> CompanyDetailResult:
        await asyncio.sleep(random.uniform(0.8, 2.0))  # simulate detail page load

        for c in MOCK_COMPANIES:
            if c["credit_code"] == company.credit_code or c["name"] == company.name:
                return CompanyDetailResult(
                    name=c["name"],
                    credit_code=c["credit_code"],
                    legal_representative=c["legal_representative"],
                    registered_capital=c["registered_capital"],
                    establish_date=c["establish_date"],
                    address=c["address"],
                    business_scope=c["business_scope"],
                    status=c["status"],
                    industry=c["industry"],
                    phone=c["phone"],
                    email=c["email"],
                    website=c["website"],
                    source=self.source_name,
                    source_url=company.source_url,
                )
        # Return what we have if no match
        return CompanyDetailResult(
            name=company.name,
            credit_code=company.credit_code,
            source=self.source_name,
            source_url=company.source_url,
        )
