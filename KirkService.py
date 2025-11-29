import requests
import base64
from io import BytesIO
import os
from PIL import Image


class KirkiFAI:
    def __init__(self):
        self.headers_download = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "TE": "trailers",
        }

        self.headers_kirkify = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "*/*",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://kirkify.wtf/",
            "Origin": "https://kirkify.wtf",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
        }

        self.work_dir = os.path.dirname(os.path.abspath(__file__))

    def download_and_save_image(self, size=248):
        """Descarga una imagen de thispersondoesnotexist.com y la guarda como campania.png, reescalada a 'size'x'size'"""
        try:
            response = requests.get(
                "https://thispersondoesnotexist.com/",
                headers=self.headers_download,
                timeout=15,
            )
            response.raise_for_status()
        except Exception as e:
            # print("[KirkiFAI] Error descargando imagen de thispersondoesnotexist:", repr(e))
            try:
                # print("[KirkiFAI] response (if available):", getattr(e, "response", None))
                pass
            except Exception:
                pass
            raise RuntimeError(f"Failed to download image: {e}")

        # Guardar imagen como campania.png
        campania_path = os.path.join(self.work_dir, "campania.png")
        try:
            with open(campania_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            # print("[KirkiFAI] Error guardando campania.png:", repr(e))
            pass
            raise RuntimeError(f"Failed to save campania.png: {e}")

        # Reescalar a size x size para evitar problemas de tamaño
        try:
            resized_bytes = self.resize_image_bytes(response.content, (size, size))
            with open(campania_path, "wb") as f:
                f.write(resized_bytes)
        except Exception as e:
            # print("[KirkiFAI] Error reescalando campania.png:", repr(e))
            pass
            # no fatal: seguir con la imagen original

        return response.content

    def resize_image_bytes(self, image_bytes, size=(500, 500)):
        """Redimensiona una imagen en bytes a `size` y devuelve bytes PNG."""
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                # Convertir a RGBA para preservar posible transparencia
                img = img.convert("RGBA")
                img = img.resize(size, Image.LANCZOS)
                out = BytesIO()
                img.save(out, format="PNG")
                return out.getvalue()
        except Exception as e:
            # print("[KirkiFAI] resize_image_bytes error:", repr(e))
            pass
            raise

    def kirkify_image(self, source_image_path, target_image_path, size=248):
        """Envía las imágenes a kirkify.wtf para procesarlas, reescaladas a 'size'x'size'"""
        url = "https://kirkify.wtf/api/kirkify"

        # Leer las imágenes desde los archivos y reescalarlas a size x size
        try:
            with open(source_image_path, "rb") as f:
                source_raw = f.read()
        except Exception as e:
            # print(f"[KirkiFAI] Error leyendo source image {source_image_path}:", repr(e))
            pass
            raise RuntimeError(f"Failed to read source image: {e}")

        try:
            with open(target_image_path, "rb") as f:
                target_raw = f.read()
        except Exception as e:
            # print(f"[KirkiFAI] Error leyendo target image {target_image_path}:", repr(e))
            pass
            raise RuntimeError(f"Failed to read target image: {e}")

        try:
            source_bytes = self.resize_image_bytes(source_raw, (size, size))
        except Exception:
            source_bytes = source_raw

        try:
            target_bytes = self.resize_image_bytes(target_raw, (size, size))
        except Exception:
            target_bytes = target_raw

        files = {
            "source-image": ("source.png", source_bytes, "image/png"),
            "target-image": ("campania.png", target_bytes, "image/png"),
        }

        try:
            response = requests.post(
                url, files=files, headers=self.headers_kirkify, timeout=60
            )
        except requests.exceptions.RequestException as e:
            # print("[KirkiFAI] Error al llamar a kirkify API:", repr(e))
            try:
                resp = getattr(e, "response", None)
                if resp is not None:
                    # print(f"[KirkiFAI] kirkify status: {resp.status_code}")
                    # print(f"[KirkiFAI] kirkify body: {resp.text}")
                    pass
            except Exception:
                pass
            raise RuntimeError(f"kirkify request failed: {e}")

        # Mostrar status y content-type para depuración
        # print(f"[KirkiFAI] kirkify status: {response.status_code}")
        content_type = response.headers.get("Content-Type", "")
        # print(f"[KirkiFAI] kirkify content-type: {content_type}")
        # try:
        #     body_preview = response.text[:1000]
        #     print("[KirkiFAI] kirkify body preview:", body_preview)
        # except Exception:
        #     print("[KirkiFAI] kirkify body preview not available (binary response)")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("[KirkiFAI] kirkify returned error status:", response.status_code)
            print(
                "[KirkiFAI] kirkify body:",
                getattr(response, "text", "<no text>")[:2000],
            )
            raise RuntimeError(f"kirkify returned HTTP error: {e}")

        # Procesar según el content-type
        ct = content_type.lower()
        if "application/json" in ct or (
            response.text and response.text.strip().startswith("{")
        ):
            try:
                data = response.json()
            except Exception as e:
                # print("[KirkiFAI] Error decodificando JSON de kirkify:", repr(e))
                # print("[KirkiFAI] kirkify raw response:", response.text[:2000])
                pass
                raise RuntimeError(f"Invalid JSON response from kirkify: {e}")

            if isinstance(data, dict) and "image" in data:
                return data

            # Buscar en la estructura JSON por cualquier string que parezca base64 / data URI
            def find_base64(obj):
                b64chars = set(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r"
                )
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_base64(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for v in obj:
                        res = find_base64(v)
                        if res:
                            return res
                elif isinstance(obj, str):
                    s = obj.strip()
                    if s.startswith("data:image") and "base64," in s:
                        return s
                    # heurística: cadena larga que parece base64
                    if len(s) > 200 and all((c in b64chars) for c in s):
                        return f"data:image/png;base64,{s}"
                return None

            found = find_base64(data)
            if found:
                return {"image": found}

            # print("[KirkiFAI] kirkify JSON unexpected structure:", data.keys() if isinstance(data, dict) else type(data))
            pass
            raise RuntimeError("kirkify returned JSON but no image key found")

        if "image/" in ct:
            try:
                b64 = base64.b64encode(response.content).decode("ascii")
                return {"image": f"data:image/png;base64,{b64}"}
            except Exception as e:
                # print("[KirkiFAI] Error codificando imagen binaria a base64:", repr(e))
                pass
                raise RuntimeError(f"Failed to encode image response: {e}")

        # Si no es JSON ni imagen, intentar descubrir si el body contiene el JSON como texto
        text = ""
        try:
            text = response.text
            if text.strip().startswith("{"):
                try:
                    data = response.json()
                    if isinstance(data, dict) and "image" in data:
                        return data
                except Exception:
                    pass
        except Exception:
            pass

        # print("[KirkiFAI] kirkify response unexpected, status:", response.status_code)
        # print("[KirkiFAI] kirkify headers:", response.headers)
        # print("[KirkiFAI] kirkify body (first 2000 chars):", text[:2000])
        raise RuntimeError("Unexpected kirkify response")

    async def process_image(self, size=248):
        """Descarga imagen, la guarda como campania.png y la procesa con kirkify, usando el tamaño 'size'"""
        # Descargar imagen de thispersondoesnotexist.com y guardarla con el tamaño dado
        self.download_and_save_image(size=size)

        # Rutas de las imágenes
        source_image_path = os.path.join(self.work_dir, "source.png")
        campania_image_path = os.path.join(self.work_dir, "campania.png")

        # Procesar con kirkify usando el tamaño dado
        result = self.kirkify_image(source_image_path, campania_image_path, size=size)

        return result
