# 變數設定
PYTHON = python
RUFF = ruff
PRE_COMMIT = pre-commit
SAM = sam


.PHONY: help fmt lint check test test-watch test-coverage build package deploy-dev deploy-staging deploy-prod local-start local-invoke logs clean setup install-deps

help:
	@echo "可用指令:"
	@echo "  make pre-commit  - 安裝pre-commit"
	@echo "  make fmt   - 自動格式化程式碼 (Ruff Format)"
	@echo "  make lint  - 檢查並修復程式碼錯誤與排序 Import (Ruff Check)"
	@echo "  make fix   - 一次執行格式化與修復"
	@echo "  make test  - 執行測試"
	@echo "  make test-watch - 執行測試並監控變更"
	@echo "  make test-coverage - 執行測試並產出覆蓋率報告"
	@echo "  make build - 安裝依賴並執行 lint 和 test"
	@echo "  make package - 建立 SAM package"
	@echo "  make deploy-dev - 部署到開發環境"
	@echo "  make deploy-staging - 部署到預備環境"
	@echo "  make deploy-prod - 部署到正式環境"
	@echo "  make local-start - 啟動本地 API"
	@echo "  make local-invoke - 本地執行 Lambda"
	@echo "  make logs - 查看開發環境的 Lambda log"
	@echo "  make clean - 清理專案"
	@echo "  make setup - 設定開發環境"
	@echo "  make install-deps - 安裝開發依賴"


pre-commit:
	$(PRE_COMMIT) install

fmt:
	$(RUFF) format .

lint:
	$(RUFF) check --fix .

fix: fmt lint
	@echo "✨ 程式碼已清理完畢！"

test:
	$(PYTHON) -m pytest tests/ -v

test-watch:
	$(PYTHON) -m pytest tests/ -v --watch

test-coverage:
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

build: install-deps lint test
	@echo "Build complete."

package:
	$(SAM) build --template-file infrastructure/template.yaml

deploy-dev: package
	$(SAM) deploy --config-env dev

deploy-staging: package
	$(SAM) deploy --config-env staging

deploy-prod: package
	$(SAM) deploy --config-env prod

local-start:
	$(SAM) local start-api --template-file infrastructure/template.yaml

local-invoke:
	$(SAM) local invoke LineWebhookFunction --template-file infrastructure/template.yaml

logs:
	$(SAM) logs --name LineWebhookFunction --stack-name pharaoh-line-webhook-dev --tail

clean:
	rm -rf .aws-sam/ __pycache__/ .pytest_cache/ htmlcov/ .coverage

setup: install-deps build
	@echo "Setup complete."

install-deps:
	$(PYTHON) -m pip install -r requirements-dev.txt
