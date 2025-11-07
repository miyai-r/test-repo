# log_sample.py
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    level: int = logging.INFO,
) -> logging.Logger:
    # ログフォルダ作成
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 祖先ロガーへ重複出力を防ぐ（実務でよく忘れる）

    # すでにハンドラが付いていたら重複防止のためクリア
    if logger.handlers:
        logger.handlers.clear()

    # 共通フォーマット（時刻 レベル モジュール: 行番号 - メッセージ）
    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    # ① コンソール出力（開発中の目視用）
    h_console = logging.StreamHandler()
    h_console.setLevel(level)
    h_console.setFormatter(fmt)
    logger.addHandler(h_console)

    # ② 日次ローテーションのファイル出力（運用保存用）
    #    midnightごとに log_sample.log, log_sample.log.2025-11-07 … と切り替わる
    h_file = TimedRotatingFileHandler(
        filename=Path(log_dir, "log_sample.log"),
        when="midnight",
        backupCount=7,           # 7世代保持
        encoding="cp932",        # WindowsでShift_JIS相当。UTF-8なら "utf-8"
        utc=False,
    )
    h_file.setLevel(level)
    h_file.setFormatter(fmt)
    logger.addHandler(h_file)

    return logger

# ---- ここから“業務ロジック”のつもり ----
def calc(x: int, y: int) -> int:
    log = logging.getLogger("app.calc")
    log.debug("start calc; x=%s y=%s", x, y)
    if y == 0:
        log.warning("y is 0; fallback to 1")
        y = 1
    ans = x // y
    log.info("result=%s", ans)
    return ans

def main():
    log = setup_logger(level=logging.DEBUG)  # 実務では INFO、開発は DEBUG で
    log.info("=== app start ===")

    try:
        calc(10, 2)
        calc(5, 0)     # warningが出るケース
        raise RuntimeError("dummy error")  # エラー例
    except Exception as e:
        # 例外のスタックトレース付き
        log.exception("unhandled exception: %s", e)

    log.info("=== app end ===")

if __name__ == "__main__":
    main()


