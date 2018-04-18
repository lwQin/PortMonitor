if (typeof WebSocket != 'function'){
    swal({
        type: "error",
        title: "您的浏览器版本太太太老了，请升级你的浏览器到IE11，或使用任何支持原生WebSocket的浏览器",
    })
}

new Vue({
    el: "#app",
    data() {
        return {
            config: {'server': {'host': null, 'port': null}, 'version': ''},
            music: null,
            date: null,
            server_groups: [],
            nightMode: false,
            nightModeManual: false,
            logs: [],
            ws: {'status': 0, 'client': null},
            alert: false,
            alertNum: 10,
            enableBtnNum: 15
        }
    },
    created() {
        this.initConfig()
        this.music = document.getElementById('music')
        this.date = new Date()
    },
    mounted() {
        let that = this
        setInterval(function() {
            that.heart()
            that.date = new Date()
            if (that.nightModeManual == false) {
                if (that.date.getHours() < 6 || that.date.getHours() == 23)
                    that.nightMode = true
                else
                    that.nightMode = false
            }
        }, 1000)
        setInterval(function() {
            that.getData()
        }, 3000)
        setInterval(function () {
            that.resetAlertNum()
        }, 60000 * 3)
    },
    watch: {
        nightMode(curVal, oldVal) {
            if (this.config.version != 'test') {
                if (curVal == true)
                    this.alertNum = 20
                else
                    this.alertNum = 10
            }
        }
    },
    methods: {
        initConfig() {
            let that = this
            axios.get("./config.json").then(function(res) {
                that.config.server.host = res.data.server.host
                that.config.server.port = res.data.server.port
                that.config.version = res.data.version
            })
            .then(function () {
                if (that.config.version == 'test') {
                    that.nightModeManual = true
                    that.alertNum = 1
                    that.enableBtnNum = 1
                }
            })
        },
        initServers() {
            let that = this
            axios.get("./servers.json").then(function(res) {
                let server_groups = res.data
                for(let group in server_groups) {
                    server_groups[group].forEach(function(server) {
                        server.status = '获取中'
                        server.alertErr = false
                        server.btnDisable = true
                        server.token = ''
                        server.alertNum = 0
                    })
                    that.server_groups.push({"description":group, "data": server_groups[group]})
                }
            })
        },
        initWebsocket() {
            this.ws.client = new WebSocket("ws://" + this.config.server.host+ ":" + this.config.server.port)
        },
        changeNightModel() {
            this.nightModeManual = true
        },
        heart() {
            if (this.ws.client == null) {
                this.initWebsocket()
            } else {
                this.ws.status = this.ws.client.readyState
                if (this.ws.client.readyState === this.ws.client.OPEN) {
                    if (this.server_groups.length == 0)
                        this.initServers()
                    this.ws.client.onmessage = this.websocketonmessage
                    this.ws.client.onclose = this.websocketclose
                    this.alert = false
                }
                else if (this.ws.client.readyState === this.ws.client.CLOSED) {
                    this.ws.client = null
                    if (this.alert == false) {
                        swal({
                            type: "error",
                            title: "无法与 websocket 服务端建立连接",
                        })
                        this.alert = true
                        this.music.play()
                    }
                    this.server_groups.forEach(function(group) {
                        group['data'].forEach(function(server) {
                            server.status = '获取中'
                        })
                    })
                }
            }
        },
        websocketonmessage(e) {
            const redata = JSON.parse(e.data)
            console.log(redata)
            switch(redata.type) {
                case 'DATA':
                    this.setData(redata)
                    break
                case 'TOKEN':
                    this.setToken(redata)
                    break
                case 'RESTART':
                    if (redata.msg == 'run') {
                        swal({
                            title: '脚本执行中',
                            onOpen: () => {
                                swal.showLoading()
                            }
                        })
                    } else {
                        if (redata.code != 0)
                            swal({
                                type: "error",
                                title: redata.data,
                                confirmButtonColor: "#F56C6C"
                            })
                        else
                            swal({
                                type: "success",
                                title: redata.data
                            })
                    }
                    break                    
            }
        },
        websocketsend(agentData) {
            this.ws.client.send(agentData)
        },
        websocketclose(e) {
            this.ws.client = null
            this.server_groups = []
            if (this.alert == false) {
                this.alert = true
                this.music.play()
                swal({
                    type: "error",
                    title: "与 websocket 服务端的连接已断开",
                })
                this.server_groups.forEach(function(group) {
                    group['data'].forEach(function(server) {
                        server.status = '获取中'
                    })
                })
                this.ws.status = 3
            }
        },
        getData() {
            let that = this
            if (this.ws.client != null && this.ws.client.readyState === this.ws.client.OPEN) {
                this.websocketsend("GET_DATA")
            }
        },
        setData(redata) {
            let that = this
            if(redata.code != 0) {
                swal({
                    type: "error",
                    title: "获取数据失败，请检查 Websocket 服务器"
                })
            } else {
                let data = redata.data
                data.forEach(function(d) {
                    that.server_groups.forEach(function(group) {
                        group['data'].forEach(function(server) {
                            if (server.flag == d.flag)
                                server.status = d.status
                        })
                    })
                })
            }
            that.checkServer()
        },
        checkServer(){
            let that = this
            that.server_groups.forEach(function(group) {
                group['data'].forEach(function(server) {
                    if (server.status != 'CLOSE')
                        server.alertErr = false
                    else {
                        let log = that.date.toLocaleString() + " connected to  " + server.host + ":" + server.port + " fail"
                        that.writeErrorLog(log)

                        server.alertErr = true
                        server.alertNum += 1                    
                    }

                    if (server.alertNum >= that.alertNum)
                        that.music.play()

                    if (server.alertNum >= that.enableBtnNum)
                        that.getToken(server)
                })
            })
        },
        writeErrorLog(log) {
            this.logs.push(log)
        },
        getToken(server) {
            if (server.flag == 'localserver') {
                this.websocketsend("GET_TOKEN?s=" + server.flag)
                server.btnDisable = false
            }
        },
        setToken(redata) {
            let data = redata.data
            this.server_groups.forEach(function(group) {
                group['data'].forEach(function(server) {
                    if (server.flag == data.flag)
                        server.token = data.token
                })
            })
        },
        restart(server) {
            if (server.flag == 'localserver') {
                swal({
                    text: "确定重启【" + server.description +"】吗？",
                    type: "warning",
                    showCancelButton: true,
                    cancelButtonText: '取消',
                    confirmButtonText: '确定',
                    confirmButtonColor: "#F56C6C"
                })
                .then((result) => {
                    if (result.value) {
                        this.websocketsend("RESTART?s=" + server.flag + "&t=" + server.token)
                        server.alertNum = 0
                        server.token = ''
                        server.btnDisable = true
                        console.log("重启服务 -> " + server.flag)
                    }
                })
            } else {
                swal({
                    text: "尚未接入",
                    type: "info"
                })
            }
        },
        resetAlertNum() {
            console.log("reset alert number = 0")
            this.server_groups.forEach(function(group) {
                group['data'].forEach(function(server) {
                    server.alertNum = 0
                })
            })
        }
    }
})