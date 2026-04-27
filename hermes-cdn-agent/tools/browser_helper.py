#!/usr/bin/env python
"""
Browser Helper - Shared browser automation utilities for tools
Extracts common browser-related methods to reduce code duplication
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from core.agentscope_adapter import AgentScopeModelAdapter

logger = logging.getLogger(__name__)


class BrowserHelperMixin:
    """Mixin class providing browser automation helper methods."""

    def _check_chrome_installed(self) -> bool:
        """
        检查系统是否安装了Chrome浏览器。

        Returns:
            bool: 如果Chrome已安装返回True，否则返回False
        """
        import shutil
        chrome_paths = [
            shutil.which("google-chrome"),
            shutil.which("chrome"),
            shutil.which("chromium"),
        ]
        if os.name == "posix":
            chrome_paths.extend([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ])
        return any(chrome_paths)

    def _extract_page_semantic_info(self, page, include_audio: bool = False, include_products: bool = False) -> Dict[str, Any]:
        """
        提取页面的语义信息，用于 LLM 分析。
        提取关键信息而不是完整 HTML，以提高效率和准确性。

        Args:
            page: Playwright page object
            include_audio: 是否包含audio元素（用于MP3下载）
            include_products: 是否包含商品信息（用于购物）

        Returns:
            Dict包含页面的语义信息
        """
        try:
            # 构建JavaScript代码，根据参数决定提取哪些信息
            js_code = """
                () => {
                    const info = {
                        title: document.title,
                        url: window.location.href,
                        headings: [],
                        links: [],
                        buttons: [],
                        inputs: [],
                        textContent: ''
                    };
            """

            if include_audio:
                js_code += """
                    info.audioElements = [];
                """

            if include_products:
                js_code += """
                    info.products = [];
                """

            js_code += """
                    // 提取标题
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    headings.forEach(h => {
                        const text = h.innerText.trim();
                        if (text) {
                            info.headings.push({
                                level: h.tagName.toLowerCase(),
                                text: text.substring(0, 200)
                            });
                        }
                    });

                    // 提取链接（限制数量，优先可见链接）
                    const allLinks = Array.from(document.querySelectorAll('a'));
                    const visibleLinks = allLinks.filter(link => {
                        const style = window.getComputedStyle(link);
                        return style.display !== 'none' && style.visibility !== 'hidden' &&
                               link.offsetWidth > 0 && link.offsetHeight > 0;
                    }).slice(0, 50);

                    visibleLinks.forEach(link => {
                        const text = link.innerText.trim() || link.textContent.trim();
                        const href = link.href || link.getAttribute('href') || '';
                        if (text || href) {
                            info.links.push({
                                text: text.substring(0, 100),
                                href: href.substring(0, 200),
                                hasText: !!text
                            });
                        }
                    });

                    // 提取按钮
                    const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'));
                    const visibleButtons = buttons.filter(btn => {
                        const style = window.getComputedStyle(btn);
                        return style.display !== 'none' && style.visibility !== 'hidden' &&
                               btn.offsetWidth > 0 && btn.offsetHeight > 0;
                    }).slice(0, 30);

                    visibleButtons.forEach(btn => {
                        const text = btn.innerText.trim() || btn.textContent.trim() || btn.value || btn.getAttribute('aria-label') || '';
                        if (text) {
                            info.buttons.push({
                                text: text.substring(0, 100),
                                type: btn.type || 'button'
                            });
                        }
                    });

                    // 提取输入框
                    const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="search"], input[name*="search"], input[name*="q"], textarea'));
                    const visibleInputs = inputs.filter(input => {
                        const style = window.getComputedStyle(input);
                        return style.display !== 'none' && style.visibility !== 'hidden' &&
                               input.offsetWidth > 0 && input.offsetHeight > 0;
                    }).slice(0, 20);

                    visibleInputs.forEach(input => {
                        const placeholder = input.placeholder || '';
                        const name = input.name || '';
                        const id = input.id || '';
                        info.inputs.push({
                            placeholder: placeholder.substring(0, 100),
                            name: name,
                            id: id
                        });
                    });
            """

            if include_audio:
                js_code += """
                    // 提取audio元素（可能包含MP3下载链接）
                    const audioElements = Array.from(document.querySelectorAll('audio'));
                    audioElements.forEach(audio => {
                        const src = audio.src || audio.getAttribute('src') || '';
                        const id = audio.id || '';
                        const controls = audio.hasAttribute('controls');
                        if (src) {
                            info.audioElements.push({
                                src: src.substring(0, 500),
                                id: id,
                                hasControls: controls
                            });
                        }
                    });
                """

            if include_products:
                js_code += """
                    // 尝试提取商品信息（常见购物网站的商品列表结构）
                    const productSelectors = [
                        '.item', '.product', '.goods', '.sku-item',
                        '[class*="item"]', '[class*="product"]', '[class*="goods"]',
                        '[id*="item"]', '[id*="product"]'
                    ];

                    productSelectors.forEach(selector => {
                        try {
                            const items = document.querySelectorAll(selector);
                            if (items.length > 0 && items.length < 100) {
                                Array.from(items).slice(0, 20).forEach(item => {
                                    const title = item.querySelector('a, .title, [class*="title"]')?.innerText?.trim() || '';
                                    const price = item.querySelector('.price, [class*="price"], .p-price, [class*="p-price"]')?.innerText?.trim() || '';
                                    if (title || price) {
                                        info.products.push({
                                            title: title.substring(0, 200),
                                            price: price.substring(0, 50),
                                            element: selector
                                        });
                                    }
                                });
                                if (info.products.length > 0) return; // 找到商品就停止
                            }
                        } catch (e) {}
                    });
                """

            js_code += """
                    // 提取主要文本内容（限制长度）
                    const bodyText = document.body ? document.body.innerText.trim() : '';
                    info.textContent = bodyText.substring(0, 2000);

                    return info;
                }
            """

            semantic_info = page.evaluate(js_code)
            return semantic_info
        except Exception as e:
            logger.warning(f"提取页面语义信息失败: {e}")
            result = {
                "title": page.title(),
                "url": page.url,
                "headings": [],
                "links": [],
                "buttons": [],
                "inputs": [],
                "textContent": ""
            }
            if include_audio:
                result["audioElements"] = []
            if include_products:
                result["products"] = []
            return result

    def _analyze_page_with_llm(
        self,
        page,
        task_description: str,
        context: Optional[str] = None,
        include_audio: bool = False,
        include_products: bool = False
    ) -> Dict[str, Any]:
        """
        使用 LLM 分析页面内容，理解用户意图，返回元素定位策略。

        Args:
            page: Playwright page object
            task_description: 任务描述（如"找到搜索框"、"找到下载按钮"）
            context: 额外的上下文信息（如搜索关键词、目标资源名称等）
            include_audio: 是否在提示中包含audio元素信息
            include_products: 是否在提示中包含商品信息

        Returns:
            Dict包含定位策略，格式：{"strategy": "text|role|label|...", "value": "...", "description": "..."}
        """
        if not hasattr(self, 'model') or not self.model:
            logger.warning("Model not available, cannot analyze page")
            return None

        try:
            # 提取页面语义信息
            semantic_info = self._extract_page_semantic_info(page, include_audio=include_audio, include_products=include_products)

            # 构建 LLM 提示
            prompt_parts = [
                f"你是一个网页自动化专家。分析以下网页信息，帮助定位目标元素。",
                f"",
                f"任务描述: {task_description}",
            ]

            if context:
                prompt_parts.append(f"上下文信息: {context}")

            prompt_parts.extend([
                f"",
                f"网页信息:",
                f"- 标题: {semantic_info.get('title', '')}",
                f"- URL: {semantic_info.get('url', '')}",
                f"- 主要标题: {json.dumps(semantic_info.get('headings', [])[:10], ensure_ascii=False, indent=2)}",
                f"- 链接列表（前20个）: {json.dumps(semantic_info.get('links', [])[:20], ensure_ascii=False, indent=2)}",
                f"- 按钮列表（前15个）: {json.dumps(semantic_info.get('buttons', [])[:15], ensure_ascii=False, indent=2)}",
                f"- 输入框列表（前10个）: {json.dumps(semantic_info.get('inputs', [])[:10], ensure_ascii=False, indent=2)}",
            ])

            if include_audio:
                prompt_parts.append(f"- 音频元素列表: {json.dumps(semantic_info.get('audioElements', []), ensure_ascii=False, indent=2)}")

            if include_products:
                prompt_parts.append(f"- 已检测到的商品信息（前10个）: {json.dumps(semantic_info.get('products', [])[:10], ensure_ascii=False, indent=2)}")

            prompt_parts.extend([
                f"- 页面主要文本（前500字符）: {semantic_info.get('textContent', '')[:500]}",
                f"",
                f"请分析页面内容，返回定位目标元素的策略。返回格式必须是有效的JSON：",
                f"",
                f"{{",
                f'    "strategy": "定位策略（text|role|label|placeholder|name|id|href{"|audio" if include_audio else ""}|combined）",',
                f'    "value": "定位值（具体文本、角色名、标签等）",',
                f'    "description": "为什么选择这个策略的简短说明"',
            ])

            # 根据工具类型添加不同的规则
            if include_audio:
                prompt_parts.extend([
                    f'    "fallback_strategies": ["备用策略1", "备用策略2"]',
                    f"}}",
                    f"",
                    f"定位策略说明:",
                    f'- "text": 使用元素的可见文本定位（如 text="搜索"）',
                    f'- "role": 使用ARIA角色定位（如 role="button"）',
                    f'- "label": 使用标签文本定位（如 label="搜索"）',
                    f'- "placeholder": 使用占位符文本定位（如 placeholder="请输入关键词"）',
                    f'- "name": 使用name属性定位（如 name="q"）',
                    f'- "id": 使用id属性定位（如 id="search"）',
                    f'- "href": 使用链接href定位（如 href*="search"）',
                    f'- "audio": 使用audio元素的src属性定位（如 audio[src*=".mp3"]），用于直接获取MP3下载链接',
                    f'- "combined": 组合多个条件定位',
                    f"",
                    f"重要规则:",
                    f"1. 优先选择最稳定、最明确的定位策略",
                    f"2. 如果任务描述包含具体文本（如'搜索框'），优先使用text或label策略",
                    f"3. 如果任务描述包含动作（如'下载按钮'、'搜索MP3'），必须找到可点击的元素（button、a标签、input[type='submit']等），不要选择纯文本显示元素",
                    f"4. 如果任务是'下载按钮'，优先在按钮列表和链接列表中查找，确保找到的是可点击的元素",
                    f"5. 如果任务描述包含资源名称，在链接列表中查找匹配的链接",
                    f"6. 如果任务是下载MP3文件，优先检查audioElements列表，audio元素的src属性通常就是MP3文件的直接下载链接",
                    f"7. 返回的value必须是页面中实际存在的文本或属性值",
                    f"8. 如果找不到明确的匹配，返回最可能的候选",
                    f"9. 不要假设按钮或链接有特定的名称（如'Search MP3'），而是根据功能描述找到能够完成任务的元素",
                    f"10. 关键：如果任务是'下载'，必须找到button、a标签或可点击的元素，不要选择DIV、SPAN等纯文本显示元素",
                ])
            elif include_products:
                prompt_parts.extend([
                    f'    "fallback_strategies": ["备用策略1", "备用策略2"]',
                    f"}}",
                    f"",
                    f"定位策略说明:",
                    f'- "text": 使用元素的可见文本定位（如 text="搜索"）',
                    f'- "role": 使用ARIA角色定位（如 role="button"）',
                    f'- "label": 使用标签文本定位',
                    f'- "placeholder": 使用占位符文本定位',
                    f'- "name": 使用name属性定位',
                    f'- "id": 使用id属性定位',
                    f'- "href": 使用链接href定位',
                    f'- "combined": 组合多个条件定位',
                    f"",
                    f"重要规则:",
                    f"1. 优先选择最稳定、最明确的定位策略",
                    f"2. 如果任务描述包含动作（如'搜索'、'登录'），必须找到可点击的元素（button、a标签等），不要选择纯文本显示元素",
                    f"3. 如果任务是'搜索'，优先在输入框列表和按钮列表中查找",
                    f"4. 如果任务是'登录'，优先在按钮列表中查找登录相关的按钮",
                    f"5. 返回的value必须是页面中实际存在的文本或属性值",
                    f"6. 不要假设按钮或链接有特定的名称，而是根据页面实际内容找到最相关的元素",
                ])
            else:
                prompt_parts.extend([
                    f"}}",
                    f"",
                    f"定位策略说明:",
                    f'- "text": 使用元素的可见文本定位（如 text="搜索"）',
                    f'- "role": 使用ARIA角色定位（如 role="button"）',
                    f'- "label": 使用标签文本定位（如 label="搜索"）',
                    f'- "placeholder": 使用占位符文本定位（如 placeholder="请输入关键词"）',
                    f'- "name": 使用name属性定位（如 name="q"）',
                    f'- "id": 使用id属性定位（如 id="search"）',
                    f'- "href": 使用链接href定位（如 href*="search"）',
                    f'- "combined": 组合多个条件定位',
                    f"",
                    f"重要规则:",
                    f"1. 优先选择最稳定、最明确的定位策略",
                    f"2. 如果任务描述包含具体文本（如'搜索框'），优先使用text或label策略",
                    f"3. 如果任务描述包含动作（如'下载按钮'），必须找到可点击的元素（button、a标签、input[type='submit']等），不要选择纯文本显示元素",
                    f"4. 如果任务是'下载按钮'，优先在按钮列表和链接列表中查找，确保找到的是可点击的元素",
                    f"5. 如果任务描述包含资源名称，在链接列表中查找匹配的链接",
                    f"6. 返回的value必须是页面中实际存在的文本或属性值",
                    f"7. 如果找不到明确的匹配，返回最可能的候选",
                    f"8. 关键：如果任务是'下载'，必须找到button、a标签或可点击的元素，不要选择DIV、SPAN等纯文本显示元素",
                ])

            prompt_parts.append(f"只返回JSON，不要其他文字。")
            prompt = "\n".join(prompt_parts)

            # 调用 AgentScope 模型
            try:
                response = AgentScopeModelAdapter.chat_with_model_sync(self.model, prompt)
            except TypeError as e:
                if "iterable" in str(e).lower():
                    logger.warning(f"LLM 返回 Msg 导致迭代错误，跳过本次分析: {e}")
                    return None
                raise

            # 将 response 转为 str，避免对 Msg 使用 in/迭代导致 "Msg is not iterable"
            def _msg_to_str(r):
                if r is None:
                    return ""
                if isinstance(r, str):
                    return r
                if hasattr(r, "content"):
                    c = getattr(r, "content", None)
                    if isinstance(c, str):
                        return c
                    if c is not None:
                        return str(c)
                return str(r)

            try:
                response = _msg_to_str(response)
            except TypeError:
                response = str(response) if response is not None else ""
            if not isinstance(response, str):
                response = str(response) if response is not None else ""

            # 解析 JSON 响应
            try:
                response_text = response.strip() if response else ""
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()

                strategy = json.loads(response_text)
                logger.info(f"LLM分析结果: {strategy.get('description', '')}")
                return strategy
            except json.JSONDecodeError as e:
                # 确保 response 是字符串后再切片
                response_str = str(response) if response is not None else ""
                response_preview = response_str[:200] if response_str else ""
                logger.warning(f"LLM返回的JSON解析失败: {e}, 响应: {response_preview}")
                return None

        except Exception as e:
            logger.warning(f"LLM分析页面失败: {e}")
            return None

    def _find_element_by_llm_guidance(
        self,
        page,
        task_description: str,
        context: Optional[str] = None,
        timeout: int = 10000,
        include_audio: bool = False,
        include_products: bool = False,
        wait_for_user_context: bool = False
    ) -> Optional[Any]:
        """
        根据 LLM 的指导找到页面元素。

        Args:
            page: Playwright page object
            task_description: 任务描述
            context: 额外的上下文信息
            timeout: 超时时间（毫秒）
            include_audio: 是否在分析中包含audio元素
            include_products: 是否在分析中包含商品信息
            wait_for_user_context: 是否在LLM分析失败时等待用户输入

        Returns:
            Playwright Locator对象，如果找不到返回None
        """
        # 使用 LLM 分析页面
        strategy = self._analyze_page_with_llm(
            page, task_description, context,
            include_audio=include_audio,
            include_products=include_products
        )

        if not strategy:
            if wait_for_user_context:
                # LLM分析失败，等待用户提供上下文
                user_context = self._wait_for_user_context(task_description, page.url)
                if user_context:
                    # 使用用户提供的上下文重新尝试
                    enhanced_context = f"{context or ''}\n用户提供的上下文关键词: {user_context}".strip()
                    logger.info("使用用户提供的上下文重新尝试LLM分析...")
                    strategy = self._analyze_page_with_llm(
                        page, task_description, enhanced_context,
                        include_audio=include_audio,
                        include_products=include_products
                    )

            if not strategy:
                logger.warning("LLM分析失败，尝试使用备用方法")
                return None

        strategy_type = strategy.get("strategy", "").lower()
        value = strategy.get("value", "")
        fallback_strategies = strategy.get("fallback_strategies", [])

        if not value:
            logger.warning("LLM返回的定位值为空")
            return None

        # 根据策略定位元素
        locator = None
        try:
            if strategy_type == "text":
                locator = page.locator(f'text="{value}"').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用text策略找到元素: {value}")
                    return locator
            elif strategy_type == "role":
                locator = page.locator(f'role={value}').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用role策略找到元素: {value}")
                    return locator
            elif strategy_type == "label":
                try:
                    label_locator = page.locator(f'label:has-text("{value}")').first
                    if label_locator.count() > 0:
                        label_for = label_locator.get_attribute("for")
                        if label_for:
                            locator = page.locator(f'#{label_for}').first
                        else:
                            locator = label_locator.locator('input, textarea, select').first
                            if locator.count() == 0:
                                locator = label_locator.locator('+ input, + textarea, + select').first

                        if locator and locator.count() > 0:
                            locator.wait_for(state="visible", timeout=timeout)
                            logger.info(f"使用label策略找到元素: {value}")
                            return locator
                except Exception as e:
                    logger.debug(f"label策略定位失败: {e}")
            elif strategy_type == "placeholder":
                locator = page.locator(f'input[placeholder*="{value}"]').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用placeholder策略找到元素: {value}")
                    return locator
            elif strategy_type == "name":
                locator = page.locator(f'[name="{value}"]').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用name策略找到元素: {value}")
                    return locator
            elif strategy_type == "id":
                locator = page.locator(f'#{value}').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用id策略找到元素: {value}")
                    return locator
            elif strategy_type == "href":
                locator = page.locator(f'a[href*="{value}"]').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用href策略找到元素: {value}")
                    return locator
            elif strategy_type == "class":
                # 支持CSS class选择器
                locator = page.locator(f'.{value.replace(" ", ".")}').first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=timeout)
                    logger.info(f"使用class策略找到元素: {value}")
                    return locator
            elif strategy_type == "audio" and include_audio:
                # 使用audio元素定位，获取src属性作为下载链接
                locator = page.locator(f'audio[src*="{value}"]').first if value else page.locator('audio').first
                if locator.count() > 0:
                    locator.wait_for(state="attached", timeout=timeout)
                    # 获取audio元素的src属性
                    try:
                        audio_src = locator.get_attribute("src")
                        if audio_src:
                            logger.info(f"使用audio策略找到元素，src: {audio_src}")
                            # 返回一个特殊的对象，包含下载URL
                            return {"type": "audio", "src": audio_src, "locator": locator}
                    except:
                        pass
                    logger.info(f"使用audio策略找到元素: {value}")
                    return locator
            elif strategy_type == "combined":
                # Combined策略：尝试多种方式组合定位
                strategies_to_try = [
                    ("text", value),
                    ("role", value),
                    ("name", value),
                ]
                for strategy_item in strategies_to_try:
                    try:
                        if strategy_item[0] == "text":
                            locator = page.locator(f'text="{strategy_item[1]}"').first
                        elif strategy_item[0] == "role":
                            locator = page.locator(f'role={strategy_item[1]}').first
                        elif strategy_item[0] == "name":
                            locator = page.locator(f'[name="{strategy_item[1]}"]').first
                        else:
                            continue

                        if locator.count() > 0:
                            locator.wait_for(state="visible", timeout=timeout)
                            logger.info(f"使用组合策略找到元素: {strategy_item}")
                            return locator
                    except:
                        continue

            # 如果主要策略失败，尝试备用策略
            for fallback in fallback_strategies:
                try:
                    if "text=" in fallback.lower():
                        text_value = fallback.replace("text=", "").strip('"\'')
                        locator = page.locator(f'text="{text_value}"').first
                    elif "role=" in fallback.lower():
                        role_value = fallback.replace("role=", "").strip()
                        locator = page.locator(f'role={role_value}').first
                    else:
                        continue

                    if locator.count() > 0:
                        locator.wait_for(state="visible", timeout=timeout)
                        logger.info(f"使用备用策略找到元素: {fallback}")
                        return locator
                except:
                    continue

        except Exception as e:
            logger.debug(f"定位元素时出错: {e}")

        logger.warning(f"无法使用LLM策略找到元素: {task_description}")
        return None

    def _wait_for_user_context(self, task_description: str, page_url: str) -> Optional[str]:
        """
        等待用户提供页面元素的上下文关键词。

        Args:
            task_description: 任务描述
            page_url: 当前页面URL

        Returns:
            用户提供的上下文关键词，如果用户取消则返回None
        """
        logger.warning("=" * 60)
        logger.warning("LLM分析失败，需要您的帮助")
        logger.warning("=" * 60)
        logger.warning(f"任务: {task_description}")
        logger.warning(f"页面URL: {page_url}")
        logger.warning("")
        logger.warning("请在浏览器中查看页面，并提供以下信息之一：")
        logger.warning("  - 目标元素的可见文本（如按钮上的文字）")
        logger.warning("  - 目标元素的class名称（如 'b-search-input'）")
        logger.warning("  - 目标元素的id或name属性")
        logger.warning("  - 目标元素附近的上下文关键词")
        logger.warning("")
        logger.warning("输入上下文关键词（直接回车跳过，输入 'cancel' 取消）: ")
        print("输入上下文关键词（直接回车跳过，输入 'cancel' 取消）: ", end="", flush=True)

        try:
            user_input = input().strip()
            if user_input.lower() == 'cancel':
                logger.info("用户取消了操作")
                return None
            if not user_input:
                logger.warning("未提供上下文，将跳过此步骤")
                return None
            logger.info(f"收到用户提供的上下文: {user_input}")
            return user_input
        except (EOFError, KeyboardInterrupt):
            logger.warning("用户中断了输入")
            return None
