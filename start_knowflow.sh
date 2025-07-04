#!/bin/bash

# KnowFlow 项目启动脚本
# 包括 MinerU、后端服务和前端服务的启动和管理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/home/aihistorian/workspace/KnowFlow"
MINERU_PORT=8888
BACKEND_PORT=5001
WEB_PORT=3333


# 日志文件
LOG_DIR="$PROJECT_DIR/logs"
MINERU_LOG="$LOG_DIR/mineru.log"
BACKEND_LOG="$LOG_DIR/backend.log"

# PID文件
PID_DIR="$PROJECT_DIR/pids"
MINERU_PID="$PID_DIR/mineru.pid"
BACKEND_PID="$PID_DIR/backend.pid"
WEB_PID="$PID_DIR/web.pid"

# 创建必要的目录
mkdir -p "$LOG_DIR" "$PID_DIR"

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if ss -tuln | grep -q ":$port "; then
        print_warning "$service_name 端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 等待服务启动
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_wait=30
    local count=0
    
    print_info "等待 $service_name 服务启动..."
    
    while [ $count -lt $max_wait ]; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1 || \
           curl -s "http://localhost:$port/health" > /dev/null 2>&1 || \
           curl -s "http://localhost:$port/api/health" > /dev/null 2>&1; then
            print_success "$service_name 服务已启动 (端口: $port)"
            return 0
        fi
        
        count=$((count + 1))
        sleep 1
        echo -n "."
    done
    
    echo
    print_error "$service_name 服务启动失败或超时"
    return 1
}

# 启动 MinerU 服务
start_mineru() {
    print_info "启动 MinerU 服务..."
    
    # 检查端口
    if ! check_port $MINERU_PORT "MinerU"; then
        print_error "MinerU 端口被占用，请先停止相关服务"
        return 1
    fi
    
    # 进入项目目录
    cd "$PROJECT_DIR"
    
    # 启动 MinerU
    print_info "在 mineru conda 环境中启动 MinerU..."
    
         # 使用 nohup 在后台启动
     nohup bash -c "
         source ~/anaconda3/etc/profile.d/conda.sh
         conda activate mineru
         cd web_api
         export MINERU_DEVICE_MODE=cpu
         export CUDA_VISIBLE_DEVICES=''
         exec python app.py
     " > "$MINERU_LOG" 2>&1 &
    
    # 保存PID
    echo $! > "$MINERU_PID"
    
    # 等待服务启动
    if wait_for_service $MINERU_PORT "MinerU"; then
        print_success "MinerU 服务启动成功"
        return 0
    else
        print_error "MinerU 服务启动失败，检查日志: $MINERU_LOG"
        return 1
    fi
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    
    # 检查端口
    if ! check_port $BACKEND_PORT "后端"; then
        print_error "后端端口被占用，请先停止相关服务"
        return 1
    fi
    
    # 进入项目目录
    cd "$PROJECT_DIR"
    
    # 启动后端服务
    print_info "启动 FastAPI 后端服务..."
    
         # 使用 nohup 在后台启动
     nohup bash -c "
         source venv/bin/activate && cd server &&  exec python3 app.py
     " > "$BACKEND_LOG" 2>&1 &
    
    # 保存PID
    echo $! > "$BACKEND_PID"
    
    # 等待服务启动
    if wait_for_service $BACKEND_PORT "后端"; then
        print_success "后端服务启动成功"
        return 0
    else
        print_error "后端服务启动失败，检查日志: $BACKEND_LOG"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    print_info "启动后台管理服务..."

    # 进入项目目录
    cd "$PROJECT_DIR"

    # 检查并启动后台前端 (web)
    if [ -d "web" ]; then
        print_info "启动后台管理服务(web 目录)..."
        if ! check_port $WEB_PORT "后台管理服务"; then
            print_warning "后台管理服务端口 $WEB_PORT 已被占用或启动失败"
        else
            nohup bash -c "
                cd web
                exec pnpm dev --port $WEB_PORT
            " > "$LOG_DIR/web_frontend.log" 2>&1 &
            
            echo $! > "$PID_DIR/web_frontend.pid"
            if wait_for_service $WEB_PORT "后台管理服务"; then
                print_success "后台管理服务启动成功"
            else
                print_error "后台管理服务启动失败，检查日志: $LOG_DIR/web_frontend.log"
            fi
        fi
    fi

    return 0
}


# 停止服务
stop_service() {
    local pid_file=$1
    local service_name=$2
    local port_to_kill=$3 # 新增参数：要清理的端口
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_info "停止 $service_name 服务 (PID: $pid)..."
            # 尝试使用 pkill 更可靠地杀死子进程
            pkill -P "$pid"
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "强制停止 $service_name 服务..."
                kill -9 "$pid"
            fi
            print_success "$service_name 服务已停止"
        else
            print_info "$service_name 服务可能已停止，但继续检查端口"
        fi
        rm -f "$pid_file"
    else
        print_info "$service_name 服务未运行"
    fi

    # 强制清理端口
    if [ -n "$port_to_kill" ]; then
        print_info "正在确保端口 $port_to_kill 已释放..."
        # 使用 fuser 命令强制杀死占用TCP端口的进程
        fuser -k -n tcp "$port_to_kill" > /dev/null 2>&1
        sleep 1
        if ! ss -tuln | grep -q ":$port_to_kill "; then
            print_success "端口 $port_to_kill 已成功释放"
        else
            print_warning "端口 $port_to_kill 可能未能释放，请手动检查"
        fi
    fi
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    stop_service "$WEB_PID" "管理前端" "$WEB_PORT"
    stop_service "$BACKEND_PID" "后端"
    stop_service "$MINERU_PID" "MinerU"
    print_success "所有服务已停止"
}

# 检查服务状态
check_status() {
    print_info "检查服务状态..."
    
    # 检查 MinerU
    if [ -f "$MINERU_PID" ] && kill -0 "$(cat "$MINERU_PID")" 2>/dev/null; then
        print_success "MinerU 服务运行中 (PID: $(cat "$MINERU_PID"), 端口: $MINERU_PORT)"
    else
        print_error "MinerU 服务未运行"
    fi
    
    # 检查后端
    if [ -f "$BACKEND_PID" ] && kill -0 "$(cat "$BACKEND_PID")" 2>/dev/null; then
        print_success "后端服务运行中 (PID: $(cat "$BACKEND_PID"), 端口: $BACKEND_PORT)"
    else
        print_error "后端服务未运行"
    fi
    
    # 检查后台前端
    if [ -f "$WEB_PID" ] && kill -0 "$(cat "$WEB_PID")" 2>/dev/null; then
        print_success "管理前端服务运行中 (PID: $(cat "$WEB_PID"))"
    else
        print_error "管理前端服务未运行"
    fi
    
    # 检查端口
    print_info "端口占用情况:"
    ss -tuln | grep -E ":($MINERU_PORT|$BACKEND_PORT) " || print_info "没有相关端口被占用"
}

# 查看日志
view_logs() {
    local service=$1
    
    case $service in
        "mineru")
            if [ -f "$MINERU_LOG" ]; then
                tail -n 50 "$MINERU_LOG"
            else
                print_error "MinerU 日志文件不存在"
            fi
            ;;
        "backend")
            if [ -f "$BACKEND_LOG" ]; then
                tail -n 50 "$BACKEND_LOG"
            else
                print_error "后端日志文件不存在"
            fi
            ;;
        "web")
            if [ -f "$LOG_DIR/web_frontend.log" ]; then
                tail -n 50 "$LOG_DIR/web_frontend.log"
            else
                print_error "后台前端日志文件不存在"
            fi
            ;;
        *)
            print_error "无效的服务名称。可选: mineru, backend, web"
            ;;
    esac
}

# 主函数
main() {
    case $1 in
        "start")
            print_info "启动 KnowFlow 项目..."
            print_info "项目目录: $PROJECT_DIR"
            
            # 确保在正确的目录
            cd "$PROJECT_DIR"
            
            # 依次启动服务
            if start_mineru; then
                sleep 3
                if start_backend; then
                    sleep 3
                    if start_frontend; then
                        print_success "所有服务启动成功!"
                        print_info "访问地址:"
                        print_info "  - MinerU API: http://localhost:$MINERU_PORT"
                        print_info "  - 后端 API: http://localhost:$BACKEND_PORT"
                        if [ -d "web" ]; then
                            print_info "  - 后台前端界面: 请查看 web 服务日志获取访问地址"
                        fi
                    else
                        print_error "前端服务启动失败"
                    fi
                else
                    print_error "后端服务启动失败"
                fi
            else
                print_error "MinerU 服务启动失败"
            fi
            ;;
        
        "stop")
            stop_all
            ;;
        
        "restart")
            stop_all
            sleep 3
            $0 start
            ;;
        
        "status")
            check_status
            ;;
        
        "logs")
            if [ -z "$2" ]; then
                print_error "请指定要查看的服务日志: mineru, backend, web"
                exit 1
            fi
            view_logs "$2"
            ;;
        
        "help"|*)
            echo "KnowFlow 项目管理脚本"
            echo ""
            echo "用法: $0 {start|stop|restart|status|logs|help}"
            echo ""
            echo "命令:"
            echo "  start    - 启动所有服务"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  status   - 检查服务状态"
            echo "  logs     - 查看服务日志 (mineru|backend|web)"
            echo "  help     - 显示此帮助信息"
            echo ""
            echo "服务端口:"
            echo "  - MinerU: $MINERU_PORT"
            echo "  - 后端: $BACKEND_PORT"
            echo "  - 后台前端(web): 自动分配"
            echo ""
            echo "日志文件:"
            echo "  - MinerU: $MINERU_LOG"
            echo "  - 后端: $BACKEND_LOG"
            echo "  - 后台前端(web): $LOG_DIR/web_frontend.log"
            ;;
    esac
}

# 运行主函数
main "$@" 