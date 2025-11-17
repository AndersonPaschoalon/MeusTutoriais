# 📘 **Apostila de Sistemas Operacionais Embarcados**

*(Inspirada na estrutura de “Sistemas Operacionais Modernos” — Tanenbaum & Bos)*

---

## **Parte I — Fundamentos dos Sistemas Embarcados**

### **Capítulo 1 — Introdução aos Sistemas Embarcados**

1.1 O que é um sistema embarcado
1.2 Diferenças entre sistemas embarcados e sistemas de propósito geral
1.3 Características principais (determinismo, tempo real, consumo, robustez)
1.4 Exemplos de aplicações reais
1.5 Estrutura típica de hardware embarcado
1.6 Estrutura típica de software embarcado
1.7 Sistemas bare-metal vs. sistemas com RTOS

---

### **Capítulo 2 — Arquitetura e Componentes de Hardware**

2.1 Microcontroladores vs. microprocessadores
2.2 Memória: RAM, ROM, Flash, EEPROM
2.3 Periféricos: GPIO, ADC, DAC, Timers, UART, SPI, I²C, CAN, USB
2.4 Relógios e temporizadores (RTC, SysTick, Watchdog)
2.5 Modos de operação e energia (PMU, low-power modes)
2.6 Bootloader e inicialização do sistema

*(→ Capítulo de média extensão – pode ser dividido em 2 partes se necessário.)*

---

## **Parte II — Conceitos de Sistema Operacional Aplicados ao Contexto Embarcado**

### **Capítulo 3 — Estrutura de um Sistema Operacional Embarcado**

3.1 Funções básicas de um sistema operacional
3.2 Núcleo (kernel) e camadas do sistema
3.3 Kernel monolítico, microkernel e híbrido
3.4 Chamadas de sistema e modo supervisor
3.5 Estrutura do RTOS (FreeRTOS, Zephyr, etc.)
3.6 O papel do *scheduler* e do *tick system*

---

### **Capítulo 4 — Gerenciamento de Processos e Tarefas**

4.1 Conceito de tarefa (*task* ou *thread*)
4.2 Ciclo de vida de uma tarefa
4.3 Context switching (troca de contexto)
4.4 Prioridades e classes de tarefas
4.5 Problemas clássicos (inversão de prioridade, starvation)
4.6 Comunicação e sincronização entre tarefas
4.7 Criação e destruição de tarefas

*(→ Capítulo longo: sugerido dividir em **4A – Conceitos e Estrutura** e **4B – Sincronização e Comunicação**)*

---

### **Capítulo 5 — Escalonamento e Tempo Real**

5.1 Conceitos de tempo real (hard e soft real-time)
5.2 Determinismo e latência
5.3 Escalonamento preemptivo e cooperativo
5.4 Algoritmos de escalonamento (Round Robin, RM, EDF)
5.5 Avaliação de escalonabilidade
5.6 Temporizadores e interrupções periódicas

---

### **Capítulo 6 — Interrupções e Rotinas de Serviço (ISR)**

6.1 Conceito de interrupção
6.2 Máscaras e prioridades de interrupção
6.3 Estrutura de uma ISR
6.4 Latência de interrupção e jitter
6.5 Boas práticas no tratamento de interrupções
6.6 Comunicação entre ISR e tarefas (deferimento)

---

### **Capítulo 7 — Comunicação Interprocessos (IPC)**

7.1 Conceito e importância do IPC
7.2 Mecanismos básicos: semáforos, mutexes, filas, sinais
7.3 Mailboxes e eventos
7.4 Pipes e buffers circulares
7.5 Sincronização e exclusão mútua
7.6 Deadlocks e condições de corrida

---

### **Capítulo 8 — Gerenciamento de Memória**

8.1 Tipos de memória em sistemas embarcados
8.2 Stack e heap
8.3 Alocação estática vs. dinâmica
8.4 Fragmentação de memória
8.5 Uso de MMU / MPU (Memory Protection Unit)
8.6 Técnicas para evitar vazamentos de memória

---

## **Parte III — Comunicação, Rede e Entrada/Saída**

### **Capítulo 9 — Interfaceamento e Drivers**

9.1 Estrutura de drivers em sistemas embarcados
9.2 Comunicação com periféricos via registradores
9.3 Drivers síncronos e assíncronos
9.4 Interrupções e DMA
9.5 Boas práticas de desenvolvimento de drivers

---

### **Capítulo 10 — Comunicação entre Dispositivos**

10.1 Protocolos de comunicação serial (UART, SPI, I²C, CAN)
10.2 Protocolos de rede (Ethernet, TCP/IP, LWIP)
10.3 Sincronização de tempo (NTP, PTP)
10.4 Comunicação sem fio (BLE, Wi-Fi, ZigBee, LoRa)
10.5 Integração entre camadas física, enlace e aplicação

---

## **Parte IV — Gerenciamento, Energia e Confiabilidade**

### **Capítulo 11 — Gerenciamento de Energia**

11.1 Estados de energia e modos *sleep*
11.2 Clock gating e power gating
11.3 Wake-up sources
11.4 Políticas de economia energética em RTOS
11.5 Medição e otimização de consumo

---

### **Capítulo 12 — Confiabilidade e Segurança**

12.1 Watchdog Timer
12.2 Fail-safe e fail-recovery
12.3 Tolerância a falhas
12.4 CRC, checagem de integridade e ECC
12.5 Segurança de firmware (assinatura e criptografia)

---

## **Parte V — Desenvolvimento e Implementação**

### **Capítulo 13 — Desenvolvimento de Firmware**

13.1 Estrutura típica de um projeto embarcado
13.2 Compilação, linkagem e geração de imagem
13.3 Bootloader e atualização OTA
13.4 Organização de memória e seções (.text, .bss, .data)
13.5 Testes e depuração (debug serial, JTAG, SWD)

---

### **Capítulo 14 — Ferramentas e Ambientes**

14.1 IDEs e toolchains (GCC, CMake, PlatformIO, etc.)
14.2 Simuladores e emuladores
14.3 Monitores seriais e logs
14.4 Sistemas de versionamento e CI/CD embarcado
14.5 Integração com hardware-in-the-loop (HIL)

---

## **Parte VI — Estudo de Casos e Aplicações**

### **Capítulo 15 — Estudo de Casos Práticos**

15.1 Sistema de aquisição de dados com FreeRTOS
15.2 Controle de motor em tempo real
15.3 Monitoramento IoT com MQTT e LWIP
15.4 Implementação de watchdog e fail-safe
15.5 Integração de sensores e atuadores

### Capítulo 16 — Estudos de Caso em Plataformas Reais

16.1 Arduino: bare-metal e temporização
16.2 Raspberry Pi: Linux embarcado e drivers no espaço do usuário
16.3 PlayStation 1: arquitetura MIPS, BIOS e DMA na prática

---

## **Parte VII — Conceitos Avançados e Tendências**

### **Capítulo 17 — Sistemas Embarcados Avançados**

17.1 Sistemas multicore e SMP em tempo real
17.2 Sistemas embarcados com Linux (Yocto, Buildroot)
17.3 Virtualização e contêineres embarcados
17.4 Segurança e atualização contínua de firmware (OTA segura)
17.5 Computação embarcada e IA de borda (TinyML)

---

## **Apêndices**

A. Glossário de Siglas e Termos Técnicos
B. Tabela de interrupções típicas por arquitetura
C. Estruturas de dados comuns em RTOS
D. Computação Gráfica para o Capítulo 16.3 (For Dummies)
E. Referências e bibliografia recomendada

