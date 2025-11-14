# **Capítulo 8 — Gerenciamento de Memória**

*“Nada causa mais dores de cabeça em sistemas embarcados do que memória. Ela é pouca, preciosa e implacável com erros.” – em estilo Andrew S. Tanenbaum*

---

## **8.1 Tipos de memória em sistemas embarcados**

Em sistemas embarcados, a memória não é um recurso abundante ou homogêneo, como nos desktops modernos. Pelo contrário, ela costuma ser escassa, segmentada e especializada. Assim, entender os tipos de memória disponíveis é essencial para projetar software eficiente e seguro.

#### **ROM / Flash**

Armazena código e dados constantes.

* É não volátil.
* Em MCUs típicos (ARM Cortex-M, PIC, AVR), o programa é executado diretamente a partir da Flash (*eXecute In Place* – XIP).
* A regravação é lenta e feita em blocos.

#### **RAM**

Usada para variáveis, pilha, buffers e estruturas de runtime. Dividida em:

* **SRAM** – rápida, estável, mas cara e limitada.
* **DRAM** – comum em SoCs maiores; exige controladoras e refrescamento periódico.

#### **EEPROM**

Para pequenos dados persistentes (configurações, calibrações).
Leitura rápida; escrita lenta e limitada em ciclos.

#### **Memória mapeada em registradores**

Regiões especiais usadas para acessar periféricos, por exemplo:

```c
#define GPIOA_ODR  (*(volatile uint32_t*)0x48000014)
```

Essas áreas não são RAM comum — escrever nelas conversa diretamente com hardware.

#### **Memória cache**

Em MCUs mais sofisticadas (ARM Cortex-A), caches L1/L2 influenciam fortemente o desempenho.
Um problema clássico de RTOS: “cache é rápido, mas não é determinístico”.

Em sistemas de tempo real rígido, muitas vezes o cache é reduzido, travado ou cuidadosamente configurado para evitar jitter.

---

## **8.2 Stack e heap**

#### **Stack (pilha)**

A pilha é usada para variáveis locais, parâmetros e retorno de funções. O ponteiro de pilha (SP) cresce e diminui automaticamente.

No ARM Cortex-M, por exemplo, a entrada de uma função frequentemente gera instruções como:

```asm
push {r4, r5, lr}   ; salva registradores
sub sp, sp, #16     ; reserva espaço para variáveis locais
```

Vantagens:

* extremamente rápida
* totalmente determinística
* não fragmenta

Desvantagens:

* tamanho fixo
* erros são catastróficos (stack overflow)

#### **Heap**

O *heap* é a área destinada à alocação dinâmica (`malloc`, `free`).
É flexível, mas vem com problemas:

* fragmentação
* imprevisibilidade do tempo de execução
* risco de vazamento

Um exemplo mínimo de alocação em C:

```c
int *p = malloc(sizeof(int) * 100);
if (p == NULL) {
    // falha por falta de memória
}
```

Em MCUs pequenos, muitos desenvolvedores simplesmente **evitam heap completamente**, usando apenas alocação estática e pilha.

---

## **8.3 Alocação estática vs. dinâmica**

#### **Alocação estática**

Feita em *compile time*:

```c
static uint8_t buffer[256];
```

Vantagens:

* determinística
* zero fragmentação
* não falha em runtime (a menos que você consuma toda RAM de início)

Usada massivamente em RTOS.

#### **Alocação dinâmica**

Exemplo com FreeRTOS:

```c
TaskHandle_t h;
xTaskCreate(task_fn, "t1", 256, NULL, 1, &h);
```

Internamente, FreeRTOS usa um de seus *heap allocators*, que vão desde um simples **heap_1.c** (sem *free*) até **heap_5.c** (com múltiplas regiões).

Em sistemas mais complexos (Linux, Zephyr), o uso de heap é comum — mas deve vir acompanhado de monitoramento.

#### **Quando usar qual?**

| Critério       | Estática         | Dinâmica                   |
| -------------- | ---------------- | -------------------------- |
| Determinismo   | Excelente        | Ruim a moderado            |
| Uso de memória | Pode desperdiçar | Ajusta conforme necessário |
| Simplicidade   | Alta             | Baixa                      |
| Escalabilidade | Difícil          | Boa                        |

A decisão depende do tipo de sistema:

* **Tempo real rígido** → prefira estática
* **Aplicações ricas (ex: IoT Linux/RTOS grande)** → dinâmica é inevitável

---

## **8.4 Fragmentação de memória**

Fragmentação ocorre quando pequenas lacunas de memória se espalham pelo heap, impedindo alocações maiores.

#### **Fragmentação externa**

Memória livre existe, mas está em blocos não contíguos.

#### **Fragmentação interna**

Uma alocação desperdiça espaço dentro de um bloco maior do que o necessário.

#### **Exemplo real (simples):**

```c
// Suponha um heap de 100 bytes
p1 = malloc(20);   // usa 20
p2 = malloc(30);   // usa 30
free(p1);          // liberta buraco de 20
p3 = malloc(25);   // falha! apesar de 50 bytes estarem livres
```

Isso pode ser devastador em sistemas embarcados.

#### **Mitigação**

1. Evitar malloc/free em runtime.
2. Usar *pools* de memória: blocos fixos.

Exemplo de pool simples:

```c
#define BLOCK_SIZE 32
#define BLOCK_COUNT 16
static uint8_t pool[BLOCK_SIZE * BLOCK_COUNT];
static uint8_t used[BLOCK_COUNT];

void *alloc_block() {
    for (int i = 0; i < BLOCK_COUNT; i++) {
        if (!used[i]) {
            used[i] = 1;
            return &pool[i * BLOCK_SIZE];
        }
    }
    return NULL;
}

void free_block(void *p) {
    size_t idx = ((uint8_t*)p - pool) / BLOCK_SIZE;
    used[idx] = 0;
}
```

Essa técnica elimina fragmentação completamente.

---

## **8.5 Uso de MMU / MPU (Memory Protection Unit)**

#### **MMU (Memory Management Unit)**

Encontrada em processadores mais robustos (ARM Cortex-A, x86).
Funções principais:

* Paginação
* Espaços de endereçamento separados
* Proteção avançada
* Mapeamento dinâmico de memória
* Suporte a sistemas operacionais completos (Linux)

Exemplo de uma entrada de tabela de páginas ARMv7 (simplificado):

```text
|31........12|11..10|9...5|4...0|
| Frame addr | AP   | TEX | Flags|
```

#### **MPU (Memory Protection Unit)**

Mais simples; fornece apenas **proteção**, não paginação.

Encontrada em Cortex-M0/M3/M4/M7.

Permite definir regiões como:

* somente leitura
* execução proibida
* acesso apenas a kernel/ISR

Exemplo FreeRTOS + MPU:

```c
const MemoryRegion_t xRegions[] =
{
    { pvTaskStack, ulStackSize, portMPU_REGION_READ_WRITE },
    { peripherals_base, 0x1000, portMPU_REGION_READ_ONLY },
    { NULL, 0, 0 }
};

xTaskCreateRestricted( &task_params, &task_handle );
```

Com MPU, um erro de ponteiro normalmente resulta em *HardFault* — excelente para detectar bugs.

---

## **8.6 Técnicas para evitar vazamentos de memória**

#### **1. Código sem malloc/free no ciclo principal**

Simples e eficaz.

#### **2. Pools de memória**

Como mostrado anteriormente.

#### **3. Rastreamento de alocações (debug)**

Em sistemas maiores (Linux):

```c
void *p = malloc(128);
fprintf(log, "allocated %p (128 bytes)\n", p);
```

Mas em sistemas embarcados pequenos, isso pode ser feito com arrays estáticos.

#### **4. Ferramentas de detecção**

* Linux: `valgrind`, ASan
* RTOS: hooks de alocação (FreeRTOS: `vApplicationMallocFailedHook`)

#### **5. Padrões de projeto para evitar uso incorreto**

* Ownership explícito (`who frees?`)
* Evitar múltiplos frees
* Zerar ponteiros após liberação

```c
free(p);
p = NULL;
```

#### **6. Watchdogs como última barreira**

Se ocorrer um vazamento catastrófico, o watchdog reinicia o sistema antes que a degradação se torne irreversível.

#### **7. Reuso de buffers estáticos**

Muito comum em drivers:

```c
static uint8_t rx_buf[128];
process_packet(rx_buf);
```

Nenhuma alocação → nenhum vazamento.
