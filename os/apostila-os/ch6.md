# **Capítulo 6 — Interrupções e Rotinas de Serviço (ISR)**

## **6.1 — Conceito de Interrupção**

Em um sistema computacional embarcado, poucas ideias são tão fundamentais — e tão elegantemente simples — quanto o mecanismo de **interrupções**. Tanenbaum frequentemente descrevia interrupções como “o modo do hardware avisar ao software que algo aconteceu e não está disposto a esperar educadamente a sua vez na fila”.

No coração de um microcontrolador, todas as instruções obedecem à cadência rígida do ciclo *fetch–decode–execute*. Mas, no mundo físico, sensores mudam de estado sem pedir permissão, pulsos digitais surgem sem aviso, motores exigem resposta imediata e usuários apertam botões exatamente no momento em que não deveriam (estatisticamente, eles sempre apertam no pior momento possível).

É aqui que a interrupção entra como o mensageiro urgente:

> **Ela suspende o fluxo normal da CPU para tratar um evento externo ou interno que exige atenção imediata.**

Tipo de eventos que geram interrupções:

* Um temporizador transborda
* Um byte chega pela UART
* Um sinal externo altera um GPIO
* Um erro ocorre na memória
* Um periférico finaliza uma operação (DMA completou transferência)

Na perspectiva do processador, interrupções são mecanismos de desvio automático: quando o evento ocorre, o hardware salva o estado atual (PC, registradores essenciais) e pula para uma rotina especial chamada **ISR — Interrupt Service Routine**.

É um dos pilares que transformam um simples microcontrolador em um sistema reativo, capaz de responder ao mundo em tempo real.

---

## **6.2 — Máscaras e Prioridades de Interrupção**

Se todas as interrupções fossem tratadas da mesma forma, viveríamos em caos absoluto. Assim como Tanenbaum destaca ao explicar prioridades de processos, os eventos externos também precisam de algum tipo de ordem social.

A solução:

### **Máscaras de interrupção**

Máscara é simplesmente a capacidade de *habilitar* ou *desabilitar* interrupções. Elas são fundamentais porque permitem:

* Evitar preempção enquanto um trecho crítico de código é executado
* Ignorar interrupções de baixa prioridade durante operações críticas
* Controlar interferência temporal em sistemas de tempo real

Em arquiteturas ARM Cortex-M, a interface **NVIC (Nested Vectored Interrupt Controller)** gerencia isso. Um exemplo típico para mascarar uma interrupção:

```c
NVIC_DisableIRQ(USART2_IRQn);  // Máscara: desabilita interrupções da UART2
...
NVIC_EnableIRQ(USART2_IRQn);   // Desmascara: habilita novamente
```

### **Prioridades de Interrupção**

Sistemas embarcados com multitarefa precisam de um mecanismo robusto para decidir:

> *“Se duas interrupções ocorrem ao mesmo tempo, qual delas deve ser tratada primeiro?”*

Cortex-M, por exemplo, implementa prioridades com 8, 16 ou mais níveis, dependendo do modelo.

```c
NVIC_SetPriority(EXTI0_IRQn, 1);   // Mais alta prioridade
NVIC_SetPriority(USART2_IRQn, 3);  // Menos urgente
```

A palavra *Nested* no NVIC significa que interrupções de prioridade mais alta **podem preemptar** ISR de prioridade menor, formando verdadeiras “pilhas” de interrupções aninhadas.

Em sistemas de tempo real rigorosos, a seleção de prioridades é parte crítica do projeto: um mau ordenamento pode aumentar dramaticamente a latência ou até causar perda de eventos.

---

## **6.3 — Estrutura de uma ISR**

A ISR é, como gostava de dizer Tanenbaum, “uma pequena exceção à normalidade — e como toda exceção, deve ser tratada com cuidado extremo”.

### **O que a CPU faz automaticamente ao entrar na ISR**

O hardware realiza várias operações sem intervenção do programador:

1. Salva contexto mínimo (PC, xPSR, LR…)
2. Atualiza o valor do PC para o endereço da ISR
3. Opcionalmente, bloqueia novas interrupções de mesma prioridade
4. Entra no modo handler (supervisor)

Depois disso, é o software que assume.

---

### **Formato típico de ISR em ARM Cortex-M**

```c
void EXTI0_IRQHandler(void)
{
    // 1. Limpar flag da interrupção (ESSENCIAL)
    if (EXTI->PR & EXTI_PR_PR0) {
        EXTI->PR = EXTI_PR_PR0;
    }

    // 2. Tratar o evento
    gpio_event_count++;     

    // 3. Evitar loops infinitos, sair rapidamente
}
```

Observe a primeira linha dentro da ISR:

> **Limpar a flag da interrupção.**

ISRs que não limpam suas flags imediatamente entram em uma situação desastrosa: o processador salta repetidamente para a mesma interrupção, sem permitir que o restante do sistema funcione — um dos primeiros bugs clássicos de quem progride de Arduino para programação bare-metal.

---

### **ISR em assembly (Cortex-M3)**

*(trecho reduzido, didático e não completo)*

```asm
    EXTI0_IRQHandler:
        ldr r0, =EXTI_BASE
        ldr r1, [r0, #PR_OFFSET]
        mov r2, #1
        str r2, [r0, #PR_OFFSET]     ; Clear pending bit

        ldr r3, =gpio_event_count
        ldr r4, [r3]
        add r4, r4, #1
        str r4, [r3]

        bx lr
```

Esse fragmento ilustra algo essencial:

* ISRs devem ser curtas
* Devem alterar o mínimo de registradores
* Devem limpar flags imediatamente
* Devem retornar rapidamente

---

### **Idiomas de ISRs em sistemas maiores (Linux)**

Em sistemas embarcados baseados em Linux, ISRs são escritas como *interrupt handlers* registrados no kernel:

```c
static irqreturn_t my_gpio_irq_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    
    dev->counter++;
    return IRQ_HANDLED;
}
```

E são registrados assim:

```c
request_irq(gpio_irq, my_gpio_irq_handler, IRQF_TRIGGER_RISING, "mydev", dev);
```

Mesmo aqui, as regras permanecem as mesmas:

* Fazer o mínimo possível na ISR
* Preferir *deferred work*, como *tasklets*, *workqueues* ou *threaded interrupts*


## **6.4 — Latência de interrupção e jitter**

Se existe um tema que separa sistemas embarcados triviais daqueles realmente capazes de operar em tempo real, esse tema é **latência de interrupção**. Tanenbaum frequentemente lembrava que, antes de discutir filosofia ou algoritmos, precisamos medir o mundo real. E, no mundo físico, atrasos importam — às vezes, atrasos de algumas dezenas de microssegundos podem significar um motor perdendo o passo, um pacote de rede perdido ou a falha de um sistema de controle.

#### **Latência de interrupção: definição**

Latência de interrupção é o tempo entre:

1. **O instante em que o hardware sinaliza a interrupção**, e
2. **O instante em que a primeira instrução da ISR começa a ser executada.**

Ou seja:

> **É o tempo que a CPU leva para parar o que está fazendo e começar a tratar o evento.**

#### **Componentes da latência**

A latência total é composta por diversos elementos:

* **Tempo de reconhecimento pelo controlador de interrupções**
  (ex.: NVIC no ARM Cortex-M)
* **Tempo para completar a instrução atual**
  Processadores sem pipeline profundo geralmente têm latência menor.
* **Tempo para salvar contexto automático**
  PC, PSR, LR e registradores essenciais.
* **Tempo para empilhar registradores adicionais (dependendo da ISR)**
* **Tempo gasto com máscaras (se interrupções estiverem desabilitadas)**
* **Preempção por interrupções mais prioritárias**

Exemplo típico em Cortex-M3: latência mínima ~12 ciclos.
Mas, com interrupções desabilitadas por longos trechos críticos, a latência real pode facilmente subir para centenas ou milhares de ciclos — um desastre em aplicações de tempo real estrito.

---

#### **Jitter de interrupção**

Jitter é a **variação temporal** da latência.

Se hoje a ISR dispara em 10 μs, amanhã em 14 μs e em outro momento em 7 μs, temos jitter.
Sistemas de tempo real, especialmente *hard real-time*, detestam jitter. Determinismo é rei.

Fatores que causam jitter:

* Cache misses (em ARM Cortex-A)
* Desabilitação de interrupções por longos períodos
* Seções críticas mal projetadas
* Outras interrupções de maior prioridade executando primeiro
* Drivers mal escritos (infelizmente, comuns)

---

#### **Como medir latência e jitter na prática**

Método clássico usando GPIO:

1. Configurar um pino como saída
2. No início da ISR, alternar esse pino (`toggle`)
3. Observar no osciloscópio o tempo entre o evento externo e a borda gerada

Exemplo de ISR que marca início da execução no GPIO:

```c
void EXTI0_IRQHandler(void)
{
    GPIOA->ODR ^= (1 << 5);    // Toggle no início da ISR
    EXTI->PR = EXTI_PR_PR0;    // Limpar flag
}
```

Um bom sistema de tempo real apresenta jitter estável e baixo.
Um sistema com jitter alto revela gargalos ocultos ou falhas de projeto.

---

## **6.5 — Boas práticas no tratamento de interrupções**

Interrupções são uma ferramenta poderosa — e, como qualquer ferramenta poderosa, podem causar danos consideráveis quando mal utilizadas. Tanenbaum costumava alertar: *“Evite escrever código dentro de interrupções como quem escreve cozinha gourmet no meio de um incêndio — seja rápido, objetivo, eficiente e saia imediatamente.”*

#### **Regra de ouro nº 1 — ISR deve ser curta**

Nada de lógica complexa. Nada de laços longos. Nada de printf.
E muito menos alocação dinâmica de memória.

```c
void USART2_IRQHandler(void)
{
    uint8_t b = USART2->DR;  // Ler dado
    ring_buffer_push(&rx_buf, b);
    // Acabou. Processamento pesado vai para a task.
}
```

#### **Regra de ouro nº 2 — Limpar a interrupção imediatamente**

Muitos bugs nascem do atraso em limpar a flag ou do esquecimento completo.

#### **Regra de ouro nº 3 — Evitar chamadas bloqueantes**

Uma ISR nunca deve esperar nada.
Uma espera ativa ou bloqueio pode travar todo o sistema.

#### **Regra de ouro nº 4 — Prioridades bem definidas**

Evitar dar prioridade máxima a tudo, fenômeno conhecido como *“priority inflation”*.

#### **Regra de ouro nº 5 — Preempção de ISR por ISR**

Evitar permitir que ISRs de prioridade intermediária causem jitter indesejado em ISRs críticas.

#### **Regra de ouro nº 6 — Não confiar em variáveis não voláteis**

Variáveis acessadas dentro de ISRs e no código principal devem ser `volatile`.

```c
volatile uint32_t tick_count = 0;
```

Isso evita otimizações que removem leituras importantes.

#### **Regra de ouro nº 7 — Minimizar o estado global**

ISR deve tocar o mínimo possível do estado global — idealmente, só alimentar filas, buffers ou flags.

---

## **6.6 — Comunicação entre ISR e tarefas (deferimento)**

Sistemas operacionais embarcados modernos evitam que ISRs façam trabalho pesado.
A solução para isso é o chamado **deferimento de processamento**:

> **A ISR faz somente o mínimo necessário; o processamento real é delegado a uma tarefa.**

Essa é a mesma filosofia usada por Linux (*softirqs*, *tasklets*, *workqueues*) e por RTOS como FreeRTOS.

### **Estratégia geral**

A ISR:

1. Captura o evento
2. Atualiza um buffer ou flag
3. Acorda uma task ou envia mensagem para uma fila
4. Termina rapidamente

A task:

* Processa os dados
* Executa lógica pesada
* Pode bloquear, logar, formatar dados — tudo que ISRs não devem fazer

---

#### **Exemplo com FreeRTOS — usando fila**

ISR preenche uma fila com bytes recebidos pela UART:

```c
void USART2_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    uint8_t byte = USART2->DR;

    xQueueSendFromISR(uart_rx_queue, &byte, &xHigherPriorityTaskWoken);

    // Força rescheduling se uma task de maior prioridade acordou
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

Task correspondente:

```c
void uart_task(void *arg)
{
    uint8_t b;

    for (;;) {
        if (xQueueReceive(uart_rx_queue, &b, portMAX_DELAY)) {
            process_uart_byte(b);
        }
    }
}
```

O sistema permanece determinístico, responsivo e organizado.

---

#### **Buffers circulares (ring buffers)**

Um padrão extremamente comum e eficiente:
A ISR coloca dados em um ring buffer; a task consome.

Pseudocódigo:

```c
ISR:
    rb[head] = novo_dado;
    head = (head + 1) % TAM;

Task:
    while (tail != head):
        process(rb[tail]);
        tail = (tail + 1) % TAM;
```

É quase o mesmo mecanismo usado por drivers de rede e UART no Linux.

---

#### **Sinalização por semáforos**

ISR:

```c
xSemaphoreGiveFromISR(my_sem, &xHigherPriorityTaskWoken);
```

Task:

```c
xSemaphoreTake(my_sem, portMAX_DELAY);
```

Este padrão é elegante para eventos que não transportam dados, mas apenas sinalizam sua ocorrência.

---

#### **Flags voláteis**

Em sistemas bare-metal muito simples:

```c
volatile uint8_t adc_ready = 0;

void ADC_IRQHandler(void) {
    adc_value = ADC->DR;
    adc_ready = 1;
}

int main(void) {
    while (!adc_ready);
    usar_adc(adc_value);
}
```

Simples e funcional — mas limitado. O mundo real geralmente exige mecanismos mais robustos.

