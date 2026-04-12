---
created: 2026-03-18
source: claude-code
tags: [spring, DI, dependency-injection, EJB, AOP, composition-root, monkey-patching, uber-fx, instagram-django, MSA, modular-monolith, deep-research]
---

# Spring DI Deep Dive: 후속 질문 Q1~Q11 상세 답변

> 이전 Deep Research ("Spring DI vs Python/Go")에 대한 후속 질문 11개를 코드 예제와 12살 비유를 포함하여 상세 답변한 문서입니다.

---

# Part 1: 인물 및 출처 검증

Now I have enough information to compile the full report.

---

## Q1: clumsysmurf 출처 검증

### clumsysmurf는 누구인가

- **실존하는 HN 사용자 ID**: 확인됨. `https://news.ycombinator.com/user?id=clumsysmurf`
- **계정 생성일**: 2011년 7월 23일 (14년 이상 활동)
- **카르마**: 8,225점 -- HN에서 상당히 높은 편. 일반적으로 1,000 이상이면 활발한 참여자, 5,000 이상이면 오래된 고참 유저로 분류됨
- **프로필 소개**: 별도 기재 없음 (익명 유저)

**판단 근거**: 카르마 8,225는 10년 이상 꾸준히 양질의 댓글을 작성해 커뮤니티로부터 인정받았다는 의미. 일회성 유저가 아닌 신뢰할 수 있는 장기 참여자.

### 댓글의 커뮤니티 반응 (upvote, 동조 댓글)

**clumsysmurf의 핵심 주장**:
> "싱글톤 같은 단일 스코프만 있으면 수동 와이어링이 쉽다. 하지만 그렇지 않으면 스코프 관리 코드와 여러 레이어에서 같은 것을 다시 와이어링하는 작업이 금방 지루해지고, 오류가 발생하기 쉽고(다른 와이어링과 동기화가 깨짐), 보일러플레이트가 된다."

**정확한 upvote 수**: HN은 자신의 댓글이 아닌 한 정확한 포인트 수를 표시하지 않으므로 확인 불가.

**동조하는 다른 댓글들**:
| 유저 | 입장 | 요지 |
|------|------|------|
| **orobinson** | 프레임워크 옹호 | 프레임워크는 "마법"이 아니며, 좋은 디자인 패턴을 장려함 |
| **paulmd** | 프레임워크 옹호 | Spring은 정교한 변환을 수행하며 "그냥 코드"가 아님 |
| **exabrial** | 프레임워크 옹호 | CDI는 광범위한 스펙을 가지며, 12년간 일관성 제공 |
| **9dev** | 부분 동조 | 반복적인 생성자 업데이트가 결국 프레임워크를 정당화함 |

반대로 수동 DI를 옹호한 유저들:
| 유저 | 요지 |
|------|------|
| **twic** | 프레임워크 없는 와이어링은 "사소하고", "이해하기 쉬움" |
| **hot_gril** | 간단한 context struct/class로 DI 충분 |
| **javcasas** | 수동 접근이 서브컨텍스트를 가능하게 함 |
| **travisgriggs** | 왜 서드파티 프레임워크 코드를 유지보수해야 하는지 의문 |

### 판단: 개인 의견 vs 대표적 반론

**판단: "커뮤니티 내 상당수가 공유하는 실무 기반 반론"**

근거:
1. **스레드 전체 논조가 양분됨** -- James Shore의 "DI 프레임워크 불필요론"에 대해 커뮤니티가 찬반으로 갈림. 일방적 동의가 아님
2. **clumsysmurf의 논점은 독자적이지 않음** -- orobinson, paulmd, exabrial, 9dev 등 여러 유저가 비슷한 맥락(실제 복잡한 프로젝트에서 수동 와이어링의 한계)을 언급
3. **clumsysmurf의 주장은 구체적 기술 논거를 포함** -- "스코프 관리", "동기화 문제", "보일러플레이트"라는 실무에서 마주치는 구체적 문제를 지적
4. **단, "대표적 다수 의견"이라고 하기엔 반대편도 강함** -- 수동 DI 옹호 측도 상당한 지지를 받음

결론: clumsysmurf의 의견은 "한 사람의 독단적 의견"이 아니라, **DI 프레임워크의 가치를 인정하는 실무 개발자 진영의 대표적 논거 중 하나**. 다만 이 스레드에서는 반대 의견도 동등하게 존재하므로, "커뮤니티 합의"가 아닌 **"합리적 양론 중 한 축"**으로 보는 것이 정확함.

---

## Q2: Rod Johnson 인물 소개

### 경력 배경

Rod Johnson은 **호주 출신 프로그래머, 저자, 기업가**로 Spring Framework의 창시자.

**학력 (흥미로운 배경)**:
- **시드니 대학교** BA (Hons) -- Computer Science, Mathematics, **Musicology** (음악학) 전공
- **시드니 대학교 PhD** (1996) -- 음악학 박사. 논문 제목: *"Piano music in Paris under the July monarchy (1830-1848)"* (7월 왕정기 파리의 피아노 음악)
- 즉, 컴퓨터 과학자이면서 동시에 19세기 프랑스 피아노 음악을 연구한 음악학 박사

**기술 배경**: 원래 C/C++ 개발자 출신이며, Java와 J2EE 초기부터 개발자, 아키텍트, 컨설턴트로 활동.

### Spring 창시 동기

- 2002년 J2EE에 대한 책을 쓰는 과정에서 "더 나은 방법이 있다"는 확신을 갖게 됨
- 당시 Enterprise Java(특히 EJB)가 지나치게 복잡하고 무거웠음
- 책의 부록으로 약 **30,000줄의 코드**를 작성 -- 이것이 Spring의 원형
- 2003년 6월 Apache 2.0 라이선스로 공개, 2004년 3월 버전 1.0 출시
- **핵심 철학**: "경량(lightweight)", 모듈화, 의존성 주입(DI)으로 엔터프라이즈 Java 개발을 혁신

### 주요 저서

1. **"Expert One-on-One J2EE Design and Development"** (Wrox, 2002)
   - Spring Framework의 기원이 된 책
   - J2EE 설계의 best practice를 제시하며 EJB의 문제점을 지적

2. **"J2EE Development without EJB"** (Wrox, 2004, Juergen Hoeller 공저)
   - EJB 없이도 엔터프라이즈 Java 개발이 가능함을 입증
   - Spring의 철학을 본격적으로 전파한 저서

3. **"Professional Java Development with the Spring Framework"** (Wrox, 2005, Juergen Hoeller 등 공저)

### 이후 경력

| 시기 | 역할 |
|------|------|
| 2003 | SpringSource 공동 창립, CEO |
| 2009 | VMware가 SpringSource 인수 --> SVP, Application Platform |
| 2011 | VMware 퇴사, **Neo4j Inc. 회장** 취임 |
| 2011~ | 이사회 활동: Elastic, Neo Technologies, Apollo, Lightbend 등 |
| 2016 | **Atomist** 창립, CEO (소프트웨어 개발 자동화) |
| 현재 (2025) | **Embabel** CEO로 활동 중 |
| 2024-2025 | YOW! Sydney, YOW! Brisbane, GOTO Copenhagen 등 컨퍼런스 연사로 활발히 활동 |

### 출처 목록

- [Rod Johnson (programmer) - Wikipedia](https://en.wikipedia.org/wiki/Rod_Johnson_(programmer))
- [Spring Creator Rod Johnson Leaves VMware - eWeek](https://www.eweek.com/development/spring-creator-rod-johnson-leaves-vmware-makes-mark-on-java/)
- [Rod Johnson - No Fluff Just Stuff Biography](https://nofluffjuststuff.com/conference/speaker/rod_johnson)
- [Rod Johnson at Spring I/O 2025](https://2025.springio.net/speakers/rod-johnson/)
- [A Bootiful Podcast: Spring creator Dr. Rod Johnson](https://spring.io/blog/2024/09/12/spring-creator-and-cofounder-dr-rod-johnson/)
- [Rod Johnson at YOW! Sydney 2025](https://yowcon.com/sydney-2025/speakers/3923/rod-johnson)
- [Rod Johnson at GOTO Copenhagen 2025](https://gotocph.com/2025/speakers/4206/rod-johnson)
- [Rod Johnson - InfoQ Podcast](https://www.infoq.com/podcasts/johnson-spring-framework/)
- [HN Thread: item?id=34298153](https://news.ycombinator.com/item?id=34298153)
- [HN User: clumsysmurf](https://news.ycombinator.com/user?id=clumsysmurf)

---

# Part 2: 조립 문제, AOP, EJB → Spring DI (코드 예제)

Now I have all the information needed. Let me write the comprehensive response.

---

# Q3: 조립 문제 + AOP/트랜잭션 ↔ DI 관계

## 3-1: "조립 문제"가 정확히 무엇인지

### 12살 비유: 레고 조립

네가 레고로 거대한 우주선을 만든다고 상상해봐.

- **수동 조립** = 레고 조각 50개를 네가 직접 "1번을 2번 위에 끼우고, 3번을 2번 옆에 끼우고..." 하나하나 순서대로 조립하는 것. 조각이 5개면 괜찮은데, 50개가 되면 설명서가 3페이지가 되고, 하나라도 순서를 바꾸면 전체가 무너져.
- **DI Framework** = "이 설계도를 기계에 넣으면, 기계가 알아서 조각들을 찾아서 조립해주는 것." 너는 각 조각에 "나는 날개 부품이야"라는 이름표만 붙이면 됨.

**"조립 문제"란**: 객체들 사이의 의존성을 누가, 어디서, 어떻게 연결(wiring)할 것인가의 문제.

### 코드 예제: 객체 5개 - 수동 조립

```java
// ========================================
// 수동 조립 (Manual DI) - 객체 5개
// main()에서 모든 것을 직접 new하고 연결
// ========================================
public class ManualAssembly {
    public static void main(String[] args) {
        // 1. 하나하나 직접 생성
        DataSource dataSource = new MySQLDataSource("jdbc:mysql://localhost/shop");
        UserRepository userRepo = new UserRepository(dataSource);
        EmailService emailService = new EmailService("smtp.gmail.com", 587);
        OrderRepository orderRepo = new OrderRepository(dataSource);
        OrderService orderService = new OrderService(orderRepo, userRepo, emailService);

        // 사용
        orderService.createOrder(new Order("item-1", 3));
    }
}
```

5개면 "이 정도는 할 만한데?" 싶지. 이제 50개를 봐봐.

### 코드 예제: 객체 50개 - 수동 조립이 폭발하는 순간

```java
// ========================================
// 수동 조립 - 객체가 늘어나면...
// ========================================
public class ManualAssemblyHell {
    public static void main(String[] args) {
        // 인프라 계층
        DataSource dataSource = new MySQLDataSource("jdbc:mysql://localhost/shop");
        RedisClient redisClient = new RedisClient("localhost", 6379);
        KafkaProducer kafkaProducer = new KafkaProducer("localhost:9092");
        S3Client s3Client = new S3Client("us-east-1", "my-bucket");

        // Repository 계층 (각각 DataSource 필요)
        UserRepository userRepo = new UserRepository(dataSource);
        OrderRepository orderRepo = new OrderRepository(dataSource);
        ProductRepository productRepo = new ProductRepository(dataSource);
        PaymentRepository paymentRepo = new PaymentRepository(dataSource);
        ShippingRepository shippingRepo = new ShippingRepository(dataSource);
        ReviewRepository reviewRepo = new ReviewRepository(dataSource);
        CouponRepository couponRepo = new CouponRepository(dataSource);
        InventoryRepository inventoryRepo = new InventoryRepository(dataSource);

        // 캐시 계층
        UserCache userCache = new UserCache(redisClient, userRepo);
        ProductCache productCache = new ProductCache(redisClient, productRepo);
        InventoryCache inventoryCache = new InventoryCache(redisClient, inventoryRepo);

        // 외부 서비스 계층
        EmailService emailService = new EmailService("smtp.gmail.com", 587);
        SmsService smsService = new SmsService("api-key-123");
        PgService pgService = new PgService("pg-secret-key");
        ShippingApiService shippingApi = new ShippingApiService("shipping-api-key");

        // 이벤트 계층
        OrderEventPublisher orderEventPub = new OrderEventPublisher(kafkaProducer);
        PaymentEventPublisher paymentEventPub = new PaymentEventPublisher(kafkaProducer);

        // 비즈니스 서비스 계층 (여기서부터 의존성이 꼬이기 시작)
        NotificationService notiService = new NotificationService(emailService, smsService);
        CouponService couponService = new CouponService(couponRepo, userCache);
        InventoryService inventoryService = new InventoryService(inventoryCache, inventoryRepo);
        PaymentService paymentService = new PaymentService(
                paymentRepo, pgService, paymentEventPub, notiService);
        ShippingService shippingService = new ShippingService(
                shippingRepo, shippingApi, notiService);
        ProductService productService = new ProductService(
                productCache, productRepo, inventoryService, s3Client);
        ReviewService reviewService = new ReviewService(reviewRepo, userCache, productService);
        OrderService orderService = new OrderService(
                orderRepo, userCache, productService, couponService,
                paymentService, shippingService, inventoryService,
                orderEventPub, notiService);

        // ... 여기에 Controller 계층, Filter, Interceptor까지 추가하면?
        // main()이 200줄이 넘어간다.

        orderService.createOrder(new Order("item-1", 3));
    }
}
```

**문제점들:**
1. **순서 의존성**: `OrderService`를 만들려면 `PaymentService`가 먼저 있어야 하고, `PaymentService`를 만들려면 `PgService`가 먼저 있어야 함. 순서를 틀리면 컴파일 에러.
2. **변경 전파**: `DataSource` 생성자 파라미터가 바뀌면? 모든 Repository 생성 코드를 고쳐야 함.
3. **환경 분기**: 개발/스테이징/프로덕션 환경마다 다른 설정? `if-else` 지옥.
4. **테스트 불가**: 이 main()을 테스트하려면? 전부 실제 객체가 필요.

### 코드 예제: Spring DI로 같은 것을 하는 방법

```java
// ========================================
// Spring DI - 같은 50개 객체, 선언만 하면 끝
// ========================================

@Repository
public class UserRepository {
    private final DataSource dataSource;

    public UserRepository(DataSource dataSource) {  // Spring이 알아서 주입
        this.dataSource = dataSource;
    }
}

@Repository
public class OrderRepository {
    private final DataSource dataSource;

    public OrderRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }
}

@Service
public class PaymentService {
    private final PaymentRepository paymentRepo;
    private final PgService pgService;
    private final PaymentEventPublisher eventPub;
    private final NotificationService notiService;

    // 생성자가 하나면 @Autowired 생략 가능
    public PaymentService(PaymentRepository paymentRepo,
                          PgService pgService,
                          PaymentEventPublisher eventPub,
                          NotificationService notiService) {
        this.paymentRepo = paymentRepo;
        this.pgService = pgService;
        this.eventPub = eventPub;
        this.notiService = notiService;
    }
}

@Service
public class OrderService {
    private final OrderRepository orderRepo;
    private final UserCache userCache;
    private final ProductService productService;
    private final CouponService couponService;
    private final PaymentService paymentService;
    // ... 나머지 의존성들

    public OrderService(OrderRepository orderRepo,
                        UserCache userCache,
                        ProductService productService,
                        CouponService couponService,
                        PaymentService paymentService /* ... */) {
        this.orderRepo = orderRepo;
        this.userCache = userCache;
        this.productService = productService;
        this.couponService = couponService;
        this.paymentService = paymentService;
    }
}

// main()은 이게 전부:
@SpringBootApplication
public class ShopApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);
        // 끝. Spring이 알아서 50개 객체를 생성하고, 의존성 그래프를 분석해서,
        // 올바른 순서로 생성하고, 생성자에 주입해준다.
    }
}
```

**Spring이 해결하는 것:**
| 문제 | 수동 조립 | Spring DI |
|------|----------|-----------|
| 생성 순서 | 개발자가 직접 관리 | 컨테이너가 의존성 그래프 분석 후 자동 결정 |
| 변경 전파 | main() 전체 수정 | 해당 Bean 설정만 수정 |
| 환경 분기 | if-else 지옥 | `@Profile("dev")`, `@Profile("prod")` |
| 테스트 | 실제 객체 필요 | Mock 주입 가능 |
| 싱글톤 관리 | 직접 보장 | 기본이 싱글톤 스코프 |

---

## 3-2: AOP가 DI와 어떤 관련인지

### 12살 비유: 학교 교실 문에 자동 잠금장치

학교에 교실이 30개 있어. 교장선생님이 "모든 교실 문에 자동 잠금장치를 달아라"고 했어.

- **AOP 없이** = 너가 30개 교실을 돌아다니며, 각 문마다 일일이 잠금장치를 설치. 교실이 추가되면? 또 가서 달아야 해.
- **AOP** = "교실"이라는 이름표가 붙은 모든 문에 자동으로 잠금장치가 달리는 **규칙**을 만드는 것.

그런데 여기서 핵심: **문을 교체할 수 있는 권한이 있어야** 잠금장치를 달 수 있어.

- **DI 컨테이너** = 학교 관리자. 모든 교실의 문(객체)을 관리하는 사람.
- **프록시** = 원래 문과 똑같이 생겼지만, 잠금장치가 내장된 **업그레이드 문**.

관리자(DI)가 "원래 문을 빼고, 잠금장치 달린 문(프록시)으로 교체"해주는 거야. 관리자 없이는 문을 교체할 수 없으니까, **DI가 AOP의 전제 조건**인 거야.

### AOP의 동작 원리: 프록시 패턴

```
[호출자] ----> [프록시 객체] ----> [실제 객체]
                  │
                  ├─ 호출 전: 트랜잭션 시작
                  ├─ 실제 메서드 호출 위임
                  └─ 호출 후: 트랜잭션 커밋/롤백
```

Spring AOP는 **프록시 객체**를 만들어서, 원래 객체 대신 주입한다. `new`로 직접 만든 객체는 Spring이 관여할 수 없으므로 프록시를 끼워넣을 수 없다.

### 코드 예제: DI+AOP 없이 트랜잭션 관리

```java
// ========================================
// DI도 AOP도 없을 때 - 모든 메서드마다 트랜잭션 코드 반복
// ========================================
public class OrderService {
    // 직접 의존성을 찾아옴 (JNDI 룩업 또는 직접 생성)
    private DataSource dataSource = new MySQLDataSource("jdbc:mysql://localhost/shop");
    private OrderDao orderDao = new OrderDao();
    private InventoryDao inventoryDao = new InventoryDao();
    private PaymentDao paymentDao = new PaymentDao();

    public void createOrder(Order order) {
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            conn.setAutoCommit(false);  // 트랜잭션 시작

            orderDao.save(conn, order);
            inventoryDao.decrease(conn, order.getItems());

            conn.commit();  // 성공하면 커밋
        } catch (Exception e) {
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { /* 로깅 */ }
            }
            throw new RuntimeException(e);
        } finally {
            if (conn != null) {
                try { conn.close(); } catch (SQLException ex) { /* 로깅 */ }
            }
        }
    }

    public void cancelOrder(Long orderId) {
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            conn.setAutoCommit(false);  // 또 같은 코드...

            Order order = orderDao.findById(conn, orderId);
            orderDao.updateStatus(conn, orderId, "CANCELLED");
            inventoryDao.increase(conn, order.getItems());
            paymentDao.refund(conn, order.getPaymentId());

            conn.commit();  // 또 같은 코드...
        } catch (Exception e) {
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { /* ... */ }
            }
            throw new RuntimeException(e);
        } finally {
            if (conn != null) {
                try { conn.close(); } catch (SQLException ex) { /* ... */ }
            }
        }
    }

    // cancelOrder, updateOrder, deleteOrder... 메서드마다 15줄의 트랜잭션 코드가 반복
}
```

매 메서드마다 `getConnection() → setAutoCommit(false) → commit() → rollback() → close()` 보일러플레이트가 반복된다. **비즈니스 로직은 2-3줄인데, 트랜잭션 관리 코드가 12줄.**

### 코드 예제: DI+AOP로 트랜잭션 관리

```java
// ========================================
// DI + AOP - 비즈니스 로직만 남음
// ========================================
@Service
public class OrderService {
    private final OrderDao orderDao;
    private final InventoryDao inventoryDao;
    private final PaymentDao paymentDao;

    public OrderService(OrderDao orderDao,
                        InventoryDao inventoryDao,
                        PaymentDao paymentDao) {
        this.orderDao = orderDao;
        this.inventoryDao = inventoryDao;
        this.paymentDao = paymentDao;
    }

    @Transactional  // 이 한 줄이 15줄의 트랜잭션 코드를 대체
    public void createOrder(Order order) {
        orderDao.save(order);                      // 비즈니스 로직만!
        inventoryDao.decrease(order.getItems());   // Connection 전달도 불필요!
    }

    @Transactional
    public void cancelOrder(Long orderId) {
        Order order = orderDao.findById(orderId);
        orderDao.updateStatus(orderId, "CANCELLED");
        inventoryDao.increase(order.getItems());
        paymentDao.refund(order.getPaymentId());
    }
}
```

### 왜 DI가 AOP의 전제 조건인가 - 프록시 주입 과정

```java
// Spring 내부에서 일어나는 일 (개념적 코드)
// ========================================

// 1단계: Spring이 원래 OrderService를 생성
OrderService realOrderService = new OrderService(orderDao, inventoryDao, paymentDao);

// 2단계: @Transactional이 있으니 프록시를 생성
OrderService proxyOrderService = new TransactionProxy(realOrderService);
//                                  ↑ 이 프록시가 begin/commit/rollback을 자동으로 감싸줌

// 3단계: 다른 빈에게는 프록시를 주입 (DI!)
OrderController controller = new OrderController(proxyOrderService);
//                                                 ↑ 실제 객체가 아니라 프록시가 들어감!

// ★ 만약 DI가 없다면?
// OrderController가 직접 new OrderService(...)를 하면
// 프록시를 끼워넣을 방법이 없다!
```

이것이 핵심: **DI 컨테이너가 객체 생성과 주입을 제어하기 때문에, 중간에 프록시를 끼워넣을 수 있다.** `new`로 직접 만들면 프록시를 끼울 틈이 없다.

### DI와 AOP의 관계 정리

```
┌──────────────────────────────────────────────┐
│              Spring Container                 │
│                                               │
│  1. 빈 생성: new OrderService(...)             │
│  2. AOP 확인: @Transactional 있네?             │
│  3. 프록시 생성: TransactionProxy(원본)         │
│  4. 프록시를 DI로 주입: controller에 프록시 전달 │
│                                               │
│  DI가 없으면 → 프록시 끼울 곳이 없음 → AOP 불가  │
└──────────────────────────────────────────────┘
```

---

# Q4: EJB 문제점 + Spring DI 해결

## 4-1: EJB가 뭔지 (12살 비유)

**비유: 서류 3장 필수 학교**

학교에서 발표를 하려면:
1. **대본** (실제 발표 내용) -- 이것만 있으면 발표할 수 있어
2. **선생님 허가서** (Home Interface) -- "이 학생이 발표를 시작/종료할 수 있음"을 증명
3. **교실 예약서** (Remote Interface) -- "이 학생의 발표를 들을 수 있음"을 증명

발표 내용은 5분짜리인데, **서류가 3장**이야. 그리고 서류 양식이 틀리면 발표를 못해. 게다가 서류에 "학교 도장"이 찍혀있어야 하니까, **다른 학교에서는 이 서류를 쓸 수 없어** (컨테이너 종속성).

이게 EJB 2.0의 문제야.

## 4-2: EJB 2.0 코드 예제 -- 간단한 주문 서비스를 만드는데 필요한 3개 파일

### 파일 1: Home Interface (허가서)

```java
// ========================================
// OrderServiceHome.java -- "빈을 생성/찾기 위한 인터페이스"
// 클라이언트가 OrderService를 사용하려면 반드시 이걸 통해야 함
// ========================================
package com.shop.ejb;

import java.rmi.RemoteException;
import javax.ejb.CreateException;
import javax.ejb.EJBHome;

public interface OrderServiceHome extends EJBHome {

    // 빈을 생성하는 메서드 -- 반드시 CreateException, RemoteException을 던져야 함
    OrderServiceRemote create() throws CreateException, RemoteException;
}
```

### 파일 2: Remote Interface (교실 예약서)

```java
// ========================================
// OrderServiceRemote.java -- "클라이언트가 호출할 수 있는 비즈니스 메서드 선언"
// ========================================
package com.shop.ejb;

import java.rmi.RemoteException;
import javax.ejb.EJBObject;

public interface OrderServiceRemote extends EJBObject {

    // 비즈니스 메서드 -- 반드시 RemoteException을 던져야 함
    void createOrder(Order order) throws RemoteException;

    void cancelOrder(Long orderId) throws RemoteException;

    Order findOrder(Long orderId) throws RemoteException;
}
```

### 파일 3: Bean Implementation (실제 대본)

```java
// ========================================
// OrderServiceBean.java -- "실제 비즈니스 로직"
// 하지만 EJB 컨테이너가 요구하는 생명주기 메서드를 전부 구현해야 함
// ========================================
package com.shop.ejb;

import javax.ejb.SessionBean;
import javax.ejb.SessionContext;
import javax.ejb.CreateException;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.sql.DataSource;
import java.rmi.RemoteException;

public class OrderServiceBean implements SessionBean {

    private SessionContext sessionContext;
    private DataSource dataSource;
    private InventoryServiceRemote inventoryService;

    // ===== EJB 컨테이너 생명주기 콜백 (반드시 구현) =====

    public void setSessionContext(SessionContext ctx) throws RemoteException {
        this.sessionContext = ctx;
    }

    public void ejbCreate() throws CreateException {
        try {
            // 의존성을 JNDI로 직접 찾아와야 함 (Service Locator 패턴)
            InitialContext ctx = new InitialContext();
            this.dataSource = (DataSource) ctx.lookup("java:comp/env/jdbc/ShopDB");

            // 다른 EJB를 사용하려면? 또 JNDI 룩업...
            InventoryServiceHome inventoryHome =
                    (InventoryServiceHome) ctx.lookup("java:comp/env/ejb/InventoryService");
            this.inventoryService = inventoryHome.create();

        } catch (NamingException e) {
            throw new CreateException("JNDI lookup failed: " + e.getMessage());
        } catch (RemoteException e) {
            throw new CreateException("Remote error: " + e.getMessage());
        }
    }

    public void ejbRemove() throws RemoteException { }
    public void ejbActivate() throws RemoteException { }
    public void ejbPassivate() throws RemoteException { }

    // ===== 실제 비즈니스 로직 (겨우 여기서부터) =====

    public void createOrder(Order order) {
        // 드디어 비즈니스 로직...
        // 하지만 트랜잭션은 XML 배포 서술자에서 별도로 설정해야 함
        orderDao.save(order);
        inventoryService.decrease(order.getItems());
    }

    public void cancelOrder(Long orderId) {
        Order order = orderDao.findById(orderId);
        orderDao.updateStatus(orderId, "CANCELLED");
        inventoryService.increase(order.getItems());
    }

    public Order findOrder(Long orderId) {
        return orderDao.findById(orderId);
    }
}
```

### 파일 4 (보너스): XML 배포 서술자

```xml
<!-- ejb-jar.xml -- 이것도 있어야 배포 가능 -->
<ejb-jar>
    <enterprise-beans>
        <session>
            <ejb-name>OrderService</ejb-name>
            <home>com.shop.ejb.OrderServiceHome</home>
            <remote>com.shop.ejb.OrderServiceRemote</remote>
            <ejb-class>com.shop.ejb.OrderServiceBean</ejb-class>
            <session-type>Stateless</session-type>
            <transaction-type>Container</transaction-type>
        </session>
    </enterprise-beans>

    <assembly-descriptor>
        <container-transaction>
            <method>
                <ejb-name>OrderService</ejb-name>
                <method-name>*</method-name>
            </method>
            <trans-attribute>Required</trans-attribute>
        </container-transaction>
    </assembly-descriptor>
</ejb-jar>
```

**결론: 비즈니스 로직은 `createOrder`, `cancelOrder`, `findOrder` 3개 메서드뿐인데, 파일이 4개, 보일러플레이트가 전체 코드의 70% 이상.**

### EJB 2.0에서 다른 서비스를 호출하는 클라이언트 코드

```java
// 클라이언트가 OrderService를 사용하려면...
public class OrderClient {
    public void placeOrder(Order order) throws Exception {
        // 1단계: JNDI Context 생성
        InitialContext ctx = new InitialContext();

        // 2단계: Home Interface를 JNDI에서 찾기
        Object ref = ctx.lookup("java:comp/env/ejb/OrderService");

        // 3단계: 타입 캐스팅 (RMI-IIOP 호환을 위해 narrow 필요)
        OrderServiceHome home = (OrderServiceHome)
                PortableRemoteObject.narrow(ref, OrderServiceHome.class);

        // 4단계: Home에서 Remote 인스턴스 생성
        OrderServiceRemote orderService = home.create();

        // 5단계: 드디어 비즈니스 메서드 호출
        orderService.createOrder(order);
    }
}
```

**5단계를 거쳐야 메서드 하나를 호출할 수 있다.**

## 4-3: Spring으로 같은 기능 구현 (After)

```java
// ========================================
// Spring - 같은 기능, 파일 1개, POJO
// ========================================
@Service
public class OrderService {

    private final OrderDao orderDao;
    private final InventoryService inventoryService;

    // 생성자 주입 - Spring이 알아서 넣어줌
    public OrderService(OrderDao orderDao, InventoryService inventoryService) {
        this.orderDao = orderDao;
        this.inventoryService = inventoryService;
    }

    @Transactional
    public void createOrder(Order order) {
        orderDao.save(order);
        inventoryService.decrease(order.getItems());
    }

    @Transactional
    public void cancelOrder(Long orderId) {
        Order order = orderDao.findById(orderId);
        orderDao.updateStatus(orderId, "CANCELLED");
        inventoryService.increase(order.getItems());
    }

    public Order findOrder(Long orderId) {
        return orderDao.findById(orderId);
    }
}
```

```java
// 클라이언트 코드
@RestController
public class OrderController {
    private final OrderService orderService;  // Spring이 주입

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping("/orders")
    public void create(@RequestBody Order order) {
        orderService.createOrder(order);  // 그냥 호출. 끝.
    }
}
```

### Before vs After 비교

| 항목 | EJB 2.0 | Spring |
|------|---------|--------|
| 파일 수 | 4개 (Home, Remote, Bean, XML) | 1개 (POJO 클래스) |
| 의존성 획득 | JNDI 룩업 (5단계) | 생성자 주입 (자동) |
| 트랜잭션 | XML 배포 서술자 | `@Transactional` |
| 테스트 | EJB 컨테이너 필요 | `new OrderService(mockDao, mockInventory)` |
| 컨테이너 종속성 | `SessionBean` 인터페이스 강제 | 아무 인터페이스 불필요 (POJO) |
| 생명주기 메서드 | 5개 필수 구현 | 불필요 |

## 4-4: 핵심 질문 -- "EJB 설계 실패가 Spring 탄생을 이끈 것이지, DI Framework를 이끈 건 아니지 않아?"

**이 질문에 대한 솔직한 답변: 반은 맞고 반은 틀리다.**

### 맞는 부분: DI 개념 자체는 EJB와 무관하게 탄생했다

- **IoC(Inversion of Control)** 개념은 1988년 Johnson & Foote의 논문 "Designing Reusable Classes"에서 처음 등장했다.
- **DI(Dependency Injection)** 라는 용어는 2004년 1월 Martin Fowler가 "Inversion of Control Containers and the Dependency Injection pattern" 글에서 명명했다.
- DI는 소프트웨어 공학의 일반 원칙(느슨한 결합, 관심사 분리)에서 나온 것이지, EJB의 실패에서 나온 것이 아니다.

**그러므로: "EJB 실패가 DI라는 개념을 만든 것은 아니다"라는 직관은 맞다.**

### 틀린 부분: Spring은 "더 나은 EJB"가 아니라, DI를 핵심 메커니즘으로 사용하여 EJB를 대체했다

Rod Johnson이 2002년 "Expert One-on-One J2EE Design and Development"에서 EJB의 문제를 분석하고, 2003년 Spring을 오픈소스로 공개할 때, 그가 선택한 해결 방법이 바로 DI였다.

EJB의 구체적인 문제가 DI로 어떻게 해결되었는지:

```
EJB 문제                          DI로 해결
─────────────────────────────────────────────────────────
JNDI 룩업으로 의존성 획득           → DI: 컨테이너가 주입
  (Service Locator 패턴)             (의존성 역전)

EJB 컨테이너 인터페이스 강제       → DI: POJO + 생성자 주입
  (SessionBean 구현 필수)            (프레임워크 비침투적)

테스트하려면 EJB 컨테이너 필요     → DI: Mock 객체 주입 가능
  (무거운 통합 테스트만 가능)         (단위 테스트 가능)

XML 배포 서술자 지옥               → AOP: @Transactional
  (트랜잭션, 보안 설정)              (DI가 전제 조건)
```

**핵심 통찰**: Spring이 EJB를 대체할 수 있었던 이유가 "DI를 핵심 철학으로 채택했기 때문"이라는 것. DI가 없었다면 Spring은 "또 다른 EJB"가 되었을 것이다.

### DI가 아닌 다른 방식으로도 해결 가능했을까? (솔직한 언급)

**가능했을 수 있는 부분:**
- **JNDI 룩업 문제**: Service Locator 패턴을 개선하는 방식으로도 해결 가능했다. 실제로 Martin Fowler도 Service Locator와 DI를 동등한 대안으로 제시했다.
- **보일러플레이트 문제**: 어노테이션 기반 코드 생성으로 해결 가능했다 (실제로 EJB 3.0이 이 방향으로 개선됨).

**DI가 아니면 해결하기 어려운 부분:**
- **테스트 용이성**: 객체 외부에서 의존성을 주입하는 DI가 가장 자연스러운 해결책이다.
- **AOP/프록시 투명 적용**: DI 컨테이너가 객체 생성을 제어하지 않으면 프록시를 투명하게 끼울 수 없다.
- **비침투적 프레임워크**: POJO를 유지하면서 프레임워크 기능을 제공하려면, 외부에서 주입하는 DI가 거의 유일한 방법이다.

### 최종 정리

```
DI 개념의 역사        ≠    Spring의 역사
(1988~ IoC 개념)          (2002~ EJB 문제 해결)
(2004 Fowler 명명)        (2003 Spring 오픈소스)

DI는 EJB 때문에 생긴 게 아님.
하지만 DI가 "프레임워크의 핵심 철학"으로 격상된 것은
EJB의 실패가 촉매 역할을 함.

EJB 실패 → Spring 탄생 → Spring이 DI를 핵심 무기로 선택
                          → DI Framework의 대중화
```

**비유로 정리하면**: 칼(DI)은 원래부터 있었어. 하지만 EJB라는 무거운 갑옷이 너무 불편해서, Rod Johnson이 "칼 하나면 충분하다"고 증명한 거야. 칼이 EJB 때문에 발명된 건 아니지만, 칼의 가치가 증명된 건 EJB 덕분이야.

---

## Sources

- [Martin Fowler - Inversion of Control Containers and the Dependency Injection pattern (2004)](https://martinfowler.com/articles/injection.html)
- [Martin Fowler - bliki: InversionOfControl](https://martinfowler.com/bliki/InversionOfControl.html)
- [Wikipedia - Inversion of Control](https://en.wikipedia.org/wiki/Inversion_of_control)
- [Oracle - Implementing the EJB 2.1 Home Interfaces](https://docs.oracle.com/cd/E16439_01/doc.1013/e13981/ent21imp003.htm)
- [Rod Johnson - Expert One-on-One J2EE Development without EJB (Wiley)](https://www.wiley.com/en-us/Expert+One+on+One+J2EE+Development+without+EJB-p-9780764573903)
- [Spring Framework - Proxying Mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)
- [Spring Framework - AOP Proxies Introduction](https://docs.spring.io/spring-framework/reference/core/aop/introduction-proxies.html)
- [PicoContainer - Inversion of Control History](http://picocontainer.com/inversion-of-control-history.html)
- [Baeldung - Spring Bean vs EJB](https://www.baeldung.com/spring-bean-vs-ejb)
- [DZone - Dependency Injection in EJB 3](https://dzone.com/refcardz/dependency-injection-in-ejb3)

---

# Part 3: 빈 500개, Composition Root, DI 프레임워크의 가치

Now let me provide the comprehensive answer directly.

---

# Q6~Q8: 빈 500개 현실성, Composition Root, DI 프레임워크의 가치

---

## Q6-1: 정말 빈 500개가 현실적인가?

### 논리와 기준

"내가 직접 만든 클래스가 500개?"라고 생각하면 비현실적으로 느껴진다. 하지만 핵심은 **내가 만든 빈 + Spring이 자동으로 만든 빈**을 합쳐야 한다는 것이다.

### 12살 비유: 학교 운동회

운동회를 준비한다고 생각해보자.

- **내가 직접 준비하는 것**: 달리기, 줄다리기, 이인삼각 (3가지)
- **학교가 알아서 준비해주는 것**: 방송장비, 텐트, 의자, 물, 구급상자, 화장실, 주차장, 현수막, 심판 호루라기, 기록 용지, 시상식 트로피... (**수십 가지**)

내가 "종목 3개만 준비했는데?"라고 생각하지만, 운동회 전체로 보면 준비물이 수십~수백 가지인 것과 같다.

### 실제 데이터

Spring 공식 블로그에 따르면:

| 앱 유형 | 빈 개수 |
|---|---|
| 수동 구성 최소 앱 | ~51개 |
| Auto-configuration 포함 앱 | ~107개 (Actuator 미포함) |
| Web + JPA + Security + Actuator | **200~400개** |
| 엔터프라이즈 앱 (MSA 한 서비스) | **300~600개** |

`spring-boot-autoconfigure` 모듈에만 **122개의 자동 구성 클래스**가 있고, 여기에 `spring-boot-actuator-autoconfigure`가 추가된다.

### 코드로 확인하는 방법

```java
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(MyApp.class, args);
        
        String[] beanNames = ctx.getBeanDefinitionNames();
        System.out.println("총 빈 개수: " + beanNames.length);
        
        // 결과 예시 (Web + JPA + Security 기본 구성):
        // 총 빈 개수: 347
    }
}
```

또는 Actuator의 `/actuator/beans` 엔드포인트로 확인 가능:

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: beans
```

### 빈 500개의 구성 비율

```
내가 직접 정의한 빈:     50~100개  (Controller, Service, Repository 등)
Spring MVC 인프라:        30~50개   (DispatcherServlet, HandlerMapping, ViewResolver 등)  
JPA/Hibernate 인프라:     20~40개   (EntityManagerFactory, TransactionManager 등)
Security 필터 체인:       20~30개   (FilterChainProxy, AuthenticationManager 등)
Actuator:                 30~50개   (HealthEndpoint, MetricsEndpoint 등)
Auto-configured 기타:     50~100개  (ObjectMapper, RestTemplate, DataSource 등)
─────────────────────────────────
합계:                     200~370개 (중간 규모 앱)
```

**결론**: 내가 직접 만드는 빈은 50~100개지만, Spring이 알아서 만드는 인프라 빈을 합치면 수백 개가 현실적이다. "빈 500개"는 대규모 엔터프라이즈 기준이지만 과장이 아니다.

---

## Q6-2: DI Framework로 조립해도 복잡한 건 마찬가지 아닌가?

### 12살 비유: 레고 설명서 vs 레고 마스터

**수동 조립** = 레고 조각 500개를 설명서 보면서 하나씩 직접 끼우는 것
**DI 프레임워크** = "이 조각은 빨간색이고 4칸짜리야"라고 **라벨만 붙이면**, 레고 로봇이 알아서 맞는 자리에 끼워주는 것

둘 다 레고 500개짜리 모델이라 "복잡한 건 마찬가지" 맞다. 하지만:
- 수동: 조각 하나 바꾸면 설명서 전체를 다시 읽어야 함
- DI: 조각 하나 바꾸면 그 조각의 라벨만 바꾸면 됨

### 코드 비교: 수동 조립 (Composition Root)

```java
public class Application {
    public static void main(String[] args) {
        // 1단계: 인프라 설정
        HikariConfig hikariConfig = new HikariConfig();
        hikariConfig.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        hikariConfig.setUsername("admin");
        hikariConfig.setPassword("secret");
        DataSource dataSource = new HikariDataSource(hikariConfig);
        
        EntityManagerFactory emf = Persistence.createEntityManagerFactory("myPU");
        PlatformTransactionManager txManager = new JpaTransactionManager(emf);
        
        // 2단계: Repository 생성 (DataSource/EMF에 의존)
        UserRepository userRepo = new JpaUserRepository(emf);
        OrderRepository orderRepo = new JpaOrderRepository(emf);
        ProductRepository productRepo = new JpaProductRepository(emf);
        
        // 3단계: 외부 서비스 (설정에 의존)
        MailConfig mailConfig = new MailConfig("smtp.gmail.com", 587, "apikey");
        EmailService emailService = new SmtpEmailService(mailConfig);
        SmsService smsService = new TwilioSmsService("twilio-token");
        PushService pushService = new FcmPushService("fcm-key");
        
        // 4단계: 비즈니스 서비스 (Repository + 외부 서비스에 의존)
        UserService userService = new UserService(userRepo, emailService);
        ProductService productService = new ProductService(productRepo);
        OrderService orderService = new OrderService(orderRepo, userService, txManager);
        PaymentService paymentService = new PaymentService(orderService, new StripeGateway("stripe-key"));
        NotificationService notiService = new NotificationService(emailService, smsService, pushService);
        
        // 5단계: 컨트롤러 (서비스에 의존)
        UserController userCtrl = new UserController(userService);
        OrderController orderCtrl = new OrderController(orderService, paymentService);
        AdminController adminCtrl = new AdminController(userService, orderService, notiService);
        
        // ⚠️ DataSource URL이 바뀌면? → 1단계부터 연쇄적으로 확인 필요
        // ⚠️ EmailService 구현체를 바꾸면? → 3, 4, 5단계 모두 확인 필요
        // ⚠️ 새 서비스 추가하면? → 여기에 생성 코드 + 주입 코드 추가
        
        new JettyServer(8080, userCtrl, orderCtrl, adminCtrl).start();
    }
}
```

### 코드 비교: DI Framework

```java
// --- 설정은 application.yml 한 곳에 ---
// spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
// spring.mail.host=smtp.gmail.com

// --- 각 클래스는 자기 의존성만 선언 ---

@Repository
public class JpaUserRepository implements UserRepository {
    @PersistenceContext
    private EntityManager em;  // Spring이 알아서 주입
}

@Service
public class UserService {
    private final UserRepository userRepo;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepo, EmailService emailService) {
        this.userRepo = userRepo;       // Spring이 알아서 주입
        this.emailService = emailService; // Spring이 알아서 주입
    }
}

@Service
public class OrderService {
    private final OrderRepository orderRepo;
    private final UserService userService;
    
    public OrderService(OrderRepository orderRepo, UserService userService) {
        this.orderRepo = orderRepo;
        this.userService = userService;
    }
    // 끝. DataSource가 뭔지, TransactionManager가 뭔지 몰라도 됨.
}

@RestController
public class OrderController {
    private final OrderService orderService;
    private final PaymentService paymentService;
    
    public OrderController(OrderService orderService, PaymentService paymentService) {
        this.orderService = orderService;
        this.paymentService = paymentService;
    }
}
```

### 핵심 차이 3가지

| 관점 | 수동 (Composition Root) | DI Framework |
|---|---|---|
| **변경 시 영향 범위** | main() 전체를 읽고 수정 | 해당 클래스만 수정 |
| **의존성 순서 관리** | 개발자가 직접 생성 순서 보장 | 프레임워크가 의존성 그래프 분석 후 자동 정렬 |
| **새 의존성 추가** | main()에 생성 코드 + 주입 코드 추가 | 생성자에 파라미터만 추가 |

**"복잡도가 사라지는 게 아니라, 프레임워크가 대신 관리하는 것."** 이것이 핵심이다.

수동 방식은 복잡도가 main() **한 곳에 집중**되고, DI 방식은 복잡도가 **각 클래스에 분산**된다.

---

## Q6-3: Composition Root란 무엇인가?

### Mark Seemann의 정의

> **"A Composition Root is a (preferably) unique location in an application where modules are composed together."**
> 
> 모든 애플리케이션 코드는 Constructor Injection에만 의존하고, 절대 스스로 조립하지 않는다. 오직 애플리케이션의 진입점에서만 전체 객체 그래프가 조립된다.
>
> -- Mark Seemann, *Dependency Injection Principles, Practices, and Patterns*

### 12살 비유: 학교 급식실

학교 급식을 생각해보자.

- **각 반(=클래스)**: "우리는 밥이랑 반찬이 필요해"라고 말만 한다 (의존성 선언)
- **급식실(=Composition Root)**: 어떤 반에 카레를 주고, 어떤 반에 볶음밥을 줄지 **한 곳에서 결정**
- 재료가 바뀌면? 급식실의 배분표만 수정하면 됨
- 새 반이 생기면? 배분표에 한 줄 추가

앱에서는 **`main()` 함수**가 이 급식실 역할을 한다.

```
main() ← Composition Root (모든 객체를 생성하고 연결하는 단 한 곳)
 ├── new DataSource(config)
 ├── new UserRepository(dataSource)
 ├── new UserService(userRepository)
 └── new UserController(userService)
```

### DI Framework와의 관계

| | Composition Root (수동) | DI Framework |
|---|---|---|
| 조립 장소 | `main()` 안에 직접 코드로 작성 | 프레임워크가 자동으로 수행 |
| 배분표 형태 | Java 코드 (new, 생성자 호출) | 어노테이션 (@Component, @Service) |
| 본질 | **동일** — 둘 다 "한 곳에서 객체를 조립"하는 개념 |

Spring의 `ApplicationContext`가 바로 **자동화된 Composition Root**다.

---

## Q7: DI 프레임워크의 "숙련도와 무관한" 가치 4가지

### Q7-1: 라이프사이클 관리

#### DI가 하는 일

객체의 **수명**을 자동으로 관리한다. "이 객체를 한 번만 만들까, 매번 새로 만들까?"를 어노테이션 하나로 결정.

#### 12살 비유: 교실의 물건

- **싱글톤(Singleton)**: 교실에 시계 1개 — 모든 학생이 같은 시계를 봄
- **프로토타입(Prototype)**: 시험지 — 학생마다 새 시험지를 받음
- **리퀘스트 스코프(Request)**: 급식판 — 점심시간에만 쓰고 반납

#### 코드 예제

```java
// DI Framework: 어노테이션 한 줄
@Service
@Scope("singleton")  // 앱 전체에서 단 1개 (기본값)
public class UserService { }

@Component
@Scope("prototype")  // 주입될 때마다 새로 생성
public class ReportGenerator { }

@Component
@Scope("request")  // HTTP 요청마다 새 인스턴스, 요청 끝나면 소멸
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();
    // 요청이 끝나면 자동으로 GC 대상
}
```

#### 수동으로 해결하면?

```java
// 수동: 싱글톤 직접 구현
public class UserServiceHolder {
    private static UserService instance;
    
    public static synchronized UserService getInstance() {
        if (instance == null) {
            instance = new UserService(
                UserRepositoryHolder.getInstance(),
                EmailServiceHolder.getInstance()
            );
        }
        return instance;
    }
}

// 수동: Request 스코프 직접 구현
public class RequestScopeManager {
    private static final ThreadLocal<Map<Class<?>, Object>> requestBeans = 
        ThreadLocal.withInitial(HashMap::new);
    
    public static <T> T getOrCreate(Class<T> type, Supplier<T> factory) {
        return (T) requestBeans.get().computeIfAbsent(type, k -> factory.get());
    }
    
    public static void clear() {  // 필터에서 요청 끝날 때 호출해야 함
        requestBeans.remove();
    }
}
```

**판정: 설계로 해결 가능하지만 보일러플레이트가 상당히 많아진다.** 특히 Request/Session 스코프는 직접 구현하면 ThreadLocal 관리, 메모리 누수 방지 등 고려할 게 많다.

---

### Q7-2: AOP (Aspect-Oriented Programming)

#### DI가 하는 일

**횡단 관심사(Cross-cutting Concern)** — 로깅, 트랜잭션, 보안, 캐싱처럼 여러 클래스에 공통으로 필요한 기능을 **코드 수정 없이** 끼워넣는다.

#### 12살 비유: 학교 CCTV

모든 교실에서 수업이 진행되는데, 각 교실에 카메라를 설치할 필요가 있다.

- **AOP 방식**: 복도에 CCTV 1대 설치 → 모든 교실 출입을 자동 기록
- **수동 방식**: 각 교실마다 선생님이 "OO가 들어왔습니다" 일일이 기록

#### 코드 예제

```java
// DI + AOP: 어노테이션만 붙이면 프록시가 자동으로 처리
@Service
public class OrderService {
    
    @Transactional          // 자동으로 트랜잭션 시작/커밋/롤백
    @Cacheable("orders")    // 결과 자동 캐싱
    @Secured("ROLE_USER")   // 권한 없으면 자동 차단
    public Order getOrder(Long id) {
        return orderRepo.findById(id);  // 순수 비즈니스 로직만!
    }
}
```

#### 수동으로 해결하면? (데코레이터 패턴)

```java
// 원본 서비스
public class OrderServiceImpl implements OrderService {
    public Order getOrder(Long id) {
        return orderRepo.findById(id);
    }
}

// 트랜잭션 데코레이터
public class TransactionalOrderService implements OrderService {
    private final OrderService delegate;
    private final TransactionManager txManager;
    
    public Order getOrder(Long id) {
        Transaction tx = txManager.begin();
        try {
            Order result = delegate.getOrder(id);
            tx.commit();
            return result;
        } catch (Exception e) {
            tx.rollback();
            throw e;
        }
    }
}

// 캐싱 데코레이터
public class CachingOrderService implements OrderService {
    private final OrderService delegate;
    private final Cache cache;
    
    public Order getOrder(Long id) {
        Order cached = cache.get("orders:" + id);
        if (cached != null) return cached;
        Order result = delegate.getOrder(id);
        cache.put("orders:" + id, result);
        return result;
    }
}

// 보안 데코레이터
public class SecuredOrderService implements OrderService {
    private final OrderService delegate;
    
    public Order getOrder(Long id) {
        if (!SecurityContext.hasRole("ROLE_USER")) {
            throw new AccessDeniedException("권한 없음");
        }
        return delegate.getOrder(id);
    }
}

// Composition Root에서 조립 (러시안 마트료시카처럼 중첩)
OrderService orderService = 
    new SecuredOrderService(
        new CachingOrderService(
            new TransactionalOrderService(
                new OrderServiceImpl(orderRepo),
                txManager
            ),
            cache
        )
    );
// ⚠️ 서비스가 30개면? 이 중첩을 30번 반복해야 함!
```

**판정: 설계로 해결 가능하지만, 서비스 수가 많아지면 현실적으로 매우 어렵다.** 데코레이터 1개 추가할 때마다 모든 서비스의 조립 코드를 수정해야 한다. AOP는 DI 프레임워크의 가장 강력한 차별점이다.

---

### Q7-3: 선언적 트랜잭션

#### DI가 하는 일

`@Transactional` 한 줄로 "이 메서드는 트랜잭션 안에서 실행해줘"라고 **선언만** 하면, 프레임워크가 begin/commit/rollback을 자동으로 처리.

#### 12살 비유: 게임 세이브 포인트

게임에서 보스전 시작 전에 자동 세이브되고, 죽으면 자동으로 세이브 포인트로 돌아가는 것.

- **@Transactional**: 게임이 자동 세이브/자동 되돌리기를 해줌
- **수동**: 매번 "세이브하겠습니까?" 버튼을 직접 눌러야 함

#### 코드 예제

```java
// DI: 선언적 트랜잭션
@Service
public class TransferService {
    
    @Transactional  // 이 한 줄이면 끝
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepo.findById(fromId);
        Account to = accountRepo.findById(toId);
        from.withdraw(amount);   // 여기서 실패하면?
        to.deposit(amount);      // → 자동으로 전체 롤백
    }
}
```

#### 수동으로 해결하면?

```java
public class TransferService {
    private final DataSource dataSource;
    
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            conn.setAutoCommit(false);  // 트랜잭션 시작
            
            Account from = accountRepo.findById(conn, fromId);
            Account to = accountRepo.findById(conn, toId);
            from.withdraw(amount);
            to.deposit(amount);
            accountRepo.update(conn, from);
            accountRepo.update(conn, to);
            
            conn.commit();  // 성공하면 커밋
        } catch (Exception e) {
            if (conn != null) {
                try {
                    conn.rollback();  // 실패하면 롤백
                } catch (SQLException rollbackEx) {
                    // 롤백마저 실패하면?? 😱
                    logger.error("롤백 실패", rollbackEx);
                }
            }
            throw new RuntimeException(e);
        } finally {
            if (conn != null) {
                try {
                    conn.close();  // 커넥션 반환
                } catch (SQLException closeEx) {
                    logger.error("커넥션 반환 실패", closeEx);
                }
            }
        }
    }
}
// 이 try/catch/finally 패턴을 트랜잭션이 필요한 모든 메서드에 반복...
```

**판정: 설계로 해결 가능하지만, 보일러플레이트가 극심하다.** 트랜잭션이 필요한 메서드가 50개라면, 이 try/catch/finally를 50번 작성하거나 Template Method 패턴을 만들어야 한다. DI 프레임워크의 편의성이 가장 극적으로 드러나는 영역이다.

---

### Q7-4: 환경별 설정

#### DI가 하는 일

`@Profile`이나 `@ConditionalOnProperty`로 "개발 환경에서는 A, 운영 환경에서는 B"를 **선언적으로** 전환.

#### 12살 비유: 체육복 vs 교복

- 체육 시간(dev) → 체육복(H2 인메모리 DB)
- 수업 시간(prod) → 교복(PostgreSQL)
- **옷장에 라벨** 붙여두면 시간표에 따라 자동으로 꺼내 입는 것

#### 코드 예제

```java
// DI: 프로파일로 자동 전환
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()  // H2 인메모리
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
}

@Configuration
@Profile("prod")
public class ProdConfig {
    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://prod-db:5432/myapp");
        return new HikariDataSource(config);
    }
}

// 실행 시: java -jar app.jar --spring.profiles.active=prod
// 끝. 코드 수정 없이 환경 전환 완료.

// 더 세밀한 조건부 설정도 가능
@Bean
@ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
public CacheManager cacheManager() {
    return new RedisCacheManager(redisConnectionFactory);
}
```

#### 수동으로 해결하면?

```java
public class Application {
    public static void main(String[] args) {
        String env = System.getenv("APP_ENV");  // 환경변수 읽기
        
        DataSource dataSource;
        if ("prod".equals(env)) {
            HikariConfig config = new HikariConfig();
            config.setJdbcUrl("jdbc:postgresql://prod-db:5432/myapp");
            dataSource = new HikariDataSource(config);
        } else if ("staging".equals(env)) {
            HikariConfig config = new HikariConfig();
            config.setJdbcUrl("jdbc:postgresql://staging-db:5432/myapp");
            dataSource = new HikariDataSource(config);
        } else {
            dataSource = new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2).build();
        }
        
        // 캐시도 환경별로...
        CacheManager cache;
        if ("prod".equals(env) && "true".equals(System.getenv("CACHE_ENABLED"))) {
            cache = new RedisCacheManager(/*...*/);
        } else {
            cache = new NoOpCacheManager();
        }
        
        // 이메일도 환경별로...
        EmailService emailService;
        if ("prod".equals(env)) {
            emailService = new SmtpEmailService(/*...*/);
        } else {
            emailService = new FakeEmailService();  // 개발 중엔 실제 메일 안 보냄
        }
        
        // ⚠️ 환경이 4개(dev, test, staging, prod)면?
        // ⚠️ 환경별로 다른 컴포넌트가 10개면?
        // → if/else 폭발!
    }
}
```

**판정: 설계로 해결 가능하지만, 환경과 컴포넌트가 늘어나면 장황해진다.** Factory 패턴이나 Strategy 패턴으로 정리할 수 있지만, DI의 `@Profile`만큼 간결하기는 어렵다.

---

### Q7 종합 판정표

| 항목 | 설계로 해결 가능? | DI 없이 현실적? | 핵심 이유 |
|---|---|---|---|
| 라이프사이클 관리 | O | 가능하지만 불편 | Singleton/Request 스코프 직접 관리는 보일러플레이트 |
| AOP | O | **현실적으로 어려움** | 서비스 30개 x 데코레이터 3개 = 조립 코드 폭발 |
| 선언적 트랜잭션 | O | 가능하지만 불편 | try/catch/finally 반복 or Template Method 필요 |
| 환경별 설정 | O | 가능하지만 불편 | if/else 폭발 or Factory 패턴 필요 |

**핵심**: 4개 모두 "설계로 불가능"한 건 아니다. 하지만 **AOP만큼은 수동으로 하면 현실적으로 매우 고통스럽고**, 나머지 3개도 앱 규모가 커지면 보일러플레이트가 급증한다. DI 프레임워크는 이 보일러플레이트를 **숙련도와 무관하게** 제거해준다.

---

## Q8-1: "인프라 요구"란 무엇인가?

### 12살 비유: 아파트 배관 시스템

앱을 아파트라고 생각해보자.

- **내가 꾸미는 것(비즈니스 로직)**: 벽지, 가구, 인테리어
- **배관 시스템(인프라)**: 수도관, 전기선, 가스관, 인터넷 케이블

벽지를 붙이려면 벽이 있어야 하고, 벽이 있으려면 기둥이 있어야 하고, 기둥이 있으려면 기초 공사가 되어야 한다. 이 **기둥, 수도관, 전기선** 같은 것이 "인프라 요구"다.

### 구체적인 예

```
앱이 실행되려면 필요한 인프라 (= 배관 시스템)
├── DB 커넥션 풀      ← 수도관 (데이터가 흐르는 통로)
├── 트랜잭션 관리자    ← 수도 밸브 (열고 닫기 제어)
├── 캐시 시스템        ← 온수 탱크 (자주 쓰는 데이터 미리 저장)
├── 메시지 큐          ← 우편함 (비동기 메시지 전달)
├── 보안 필터          ← 현관 잠금장치 (인증/인가)
├── HTTP 서버          ← 아파트 현관 (외부 요청 수신)
└── 로깅 시스템        ← CCTV (무슨 일이 일어났는지 기록)
```

### DI 프레임워크와의 관계

인프라가 복잡할수록 DI 프레임워크가 빛난다.

```java
// 인프라가 간단한 앱 (CLI 도구):
// → main()에서 수동 조립해도 10줄이면 끝
// → DI 프레임워크 불필요

// 인프라가 복잡한 앱 (웹 서비스):
// → DB + 캐시 + 메시지큐 + 보안 + 트랜잭션 + HTTP 서버
// → 이것들의 조립과 수명 관리를 수동으로 하면 Composition Root가 수백 줄
// → DI 프레임워크가 자동 구성으로 대부분 처리
```

**"인프라 요구가 높다 = DI 프레임워크의 가치가 높다"** 라는 관계가 성립한다.

---

## Q8-2: "언어 편의성"이란 무엇인가?

### 12살 비유: 도구의 차이

같은 나무를 자르는데:
- **전기톱(Python/Go)**: 버튼만 누르면 잘린다 → DI 프레임워크 없이도 충분
- **손톱(Java)**: 힘들게 밀어야 한다 → 전동 공구(DI 프레임워크)가 있으면 훨씬 편하다

언어마다 **의존성을 교체하고 조립하는 난이도**가 다르다. 이 난이도 차이가 "언어 편의성"이다.

### Python: 함수 기본값으로 DI 끝

```python
# Python: 함수 인자 기본값 = 간이 DI
def get_user(user_id: int, repo=default_user_repo):
    return repo.find_by_id(user_id)

# 테스트할 때? 그냥 다른 repo 넣으면 됨
def test_get_user():
    fake_repo = FakeUserRepo()
    user = get_user(1, repo=fake_repo)  # DI 프레임워크 없이 교체 완료!
    assert user.name == "Alice"

# Duck typing이라 인터페이스 선언도 불필요
class FakeUserRepo:
    def find_by_id(self, user_id):  # 같은 메서드만 있으면 됨
        return User(name="Alice")
```

### Go: Implicit Interface로 자연스러운 DI

```go
// Go: 인터페이스를 "구현한다"고 선언할 필요 없음 (implicit interface)
type UserRepository interface {
    FindByID(id int) (*User, error)
}

// implements 키워드 없이, 메서드 시그니처만 맞으면 자동으로 구현체
type PostgresUserRepo struct {
    db *sql.DB
}
func (r *PostgresUserRepo) FindByID(id int) (*User, error) { /*...*/ }

// 테스트용 mock도 인터페이스 선언 없이 바로 생성
type MockUserRepo struct{}
func (r *MockUserRepo) FindByID(id int) (*User, error) {
    return &User{Name: "Alice"}, nil
}

// 생성자에서 인터페이스 받으면 DI 끝
func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}
```

### Java: 명시적 선언이 필요 → DI 프레임워크가 이것을 대신

```java
// Java: 인터페이스 명시적 선언 필수
public interface UserRepository {
    User findById(Long id);
}

// implements 명시적 선언 필수
public class JpaUserRepository implements UserRepository {
    @Override
    public User findById(Long id) { /*...*/ }
}

// 팩토리 패턴이나 DI 프레임워크 없이 교체하려면?
public class UserService {
    private final UserRepository repo;
    
    // 방법 1: 생성자 주입 (수동)
    public UserService(UserRepository repo) {
        this.repo = repo;
    }
    
    // 방법 2: 팩토리 패턴 (수동)
    public UserService() {
        this.repo = UserRepositoryFactory.create();  // 팩토리 클래스도 만들어야 함
    }
}

// Spring이 해결: 어노테이션만 붙이면 자동
@Service
public class UserService {
    private final UserRepository repo;
    
    // @Autowired 없어도 생성자 하나면 자동 주입 (Spring 4.3+)
    public UserService(UserRepository repo) {
        this.repo = repo;  // Spring이 JpaUserRepository를 찾아서 자동 주입
    }
}
```

### 언어별 DI 프레임워크 필요도

| 언어 | 인터페이스 | 타입 시스템 | DI 편의성 | DI 프레임워크 필요도 |
|---|---|---|---|---|
| **Python** | 없음 (Duck typing) | 동적 | 함수 인자 기본값으로 충분 | **낮음** |
| **Go** | 암묵적 (implicit) | 정적 | 생성자 주입으로 충분 | **낮음~중간** |
| **Java** | 명시적 (explicit) | 정적 + 엄격 | 팩토리 패턴 필요 | **높음** |
| **C#** | 명시적 (explicit) | 정적 + 엄격 | Java와 유사 | **높음** |

### 왜 이런 차이가 생기는가?

```
Python/Go가 DI 프레임워크 없이도 되는 이유:
1. Duck typing / Implicit interface → 인터페이스 선언 보일러플레이트 없음
2. 함수가 일급 객체 → 함수 자체를 의존성으로 전달 가능
3. 언어 자체가 "느슨한 결합"을 자연스럽게 지원

Java가 DI 프레임워크가 필요한 이유:
1. 모든 것이 클래스 → 간단한 의존성 교체도 클래스 + 인터페이스 필요
2. 명시적 implements → 보일러플레이트 많음
3. 엄격한 타입 체크 → 팩토리 패턴이나 DI 프레임워크로 우회
```

---

## 전체 요약: 왜 DI 프레임워크를 쓰는가?

```
DI 프레임워크 필요성 = 인프라 요구 x 언어 편의성(의 부족)

                        인프라 요구 높음
                            │
              ┌─────────────┼─────────────┐
              │             │             │
  Java 웹 서비스     Go 마이크로서비스    Python 스크립트
  (DI 프레임워크      (wire 정도면       (거의 불필요)
   거의 필수)          충분)
              │             │             │
              └─────────────┼─────────────┘
                            │
                        인프라 요구 낮음
```

**"빌더 패턴으로 충분하다"는 의문에 대한 답**: 인프라 요구가 낮고 Python/Go 같은 유연한 언어를 쓴다면 맞다. 하지만 Java로 웹 서비스를 만들고, DB + 캐시 + 보안 + 트랜잭션이 필요한 순간, DI 프레임워크 없이 Composition Root를 수동 관리하는 것은 숙련도와 무관하게 고통스럽다.

---

Sources:
- [Have you ever wondered how many 'beans' your project uses behind the scenes? - Medium](https://zgokceaynaci.medium.com/have-you-ever-wondered-how-many-beans-your-project-uses-behind-the-scenes-2803e65e1289)
- [Manual Bean Definitions in Spring Boot - Spring Blog](https://spring.io/blog/2019/01/21/manual-bean-definitions-in-spring-boot/)
- [Composition Root - Mark Seemann's Blog](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)
- [Understanding the Composition Root - Manning](https://freecontent.manning.com/dependency-injection-in-net-2nd-edition-understanding-the-composition-root/)
- [Dependency Injection Principles, Practices, and Patterns - Manning](https://www.manning.com/books/dependency-injection-principles-practices-patterns)
- [Dependency Injection with Mark Seemann - InfoQ](https://www.infoq.com/articles/DI-Mark-Seemann/)
- [Spring Boot Actuator Beans Endpoint - Spring Docs](https://docs.spring.io/spring-boot/api/rest/actuator/beans.html)

---

# Part 4: Instagram Django + MSA 회귀 트렌드

Now I have enough data to compile a comprehensive report. Let me present the findings.

---

## Q10: Instagram Django 현재 상태

### 현재 사용 여부

Instagram은 **2025-2026년 현재도 Django를 사용**하고 있다. 세계 최대 규모의 Django 배포 환경으로, 수십억 건의 일일 인터랙션을 처리한다. 단, "순정" Django가 아니라 **극도로 커스터마이징된 Django**를 운용 중이다.

### 커스텀 내용

**1. Python 런타임 자체를 교체: Cinder / CinderX**
- Meta는 Instagram Django 서비스를 위해 **CPython 자체를 포크**하여 "Cinder"를 개발했다.
- JIT 컴파일러, Static Python, 병렬 가비지 컬렉터, 경량 인터프리터 프레임 등 포함.
- Python 3.10부터는 **CinderX**라는 확장 모듈로 전환, Python 3.14부터 stock CPython에서도 지원 가능.
- CinderX는 현재 프로덕션에서 사용 중이며, PyPI에 매주 릴리스됨.

**2. Django ORM 교체: 커스텀 ORM**
- Instagram은 Django의 ORM을 **자체 커스텀 ORM으로 교체**했다.
- 이유: 대규모 샤딩이 필요해지면서 기본 ORM으로는 처리 불가.
- likes 데이터부터 마이그레이션을 시작, 2년 후 user 데이터도 이전.
- 일부 영역에서는 여전히 기본 Django ORM도 사용하지만, 대용량 데이터는 모두 커스텀 ORM.

**3. 데이터베이스: PostgreSQL + Cassandra**
- **PostgreSQL**: 사용자 프로필, 댓글, 관계, 메타데이터 등 구조화 데이터 (master-replica 아키텍처).
- **Cassandra**: 피드, 활동 로그, 분석 데이터 등 고분산 데이터.

**4. Python GC 수정 및 Immortal Objects**
- `gc.freeze()` API를 Python GC 모듈에 추가 (Python 3.7에 upstream 반영).
- **Immortal Objects**: copy-on-write를 줄여 메모리 및 CPU 효율성을 대폭 개선. 공유 메모리 사용 증가를 통해 프라이빗 메모리를 크게 절감.

**5. 커스텀 미들웨어 (Dynostats)**
- Django 미들웨어를 활용해 사용자 요청을 샘플링하여 CPU 인스트럭션 수, end-to-end 응답 시간 등 성능 메트릭을 기록하는 Dynostats 도구를 자체 개발.

**6. 프론트엔드: React + GraphQL**
- 프론트엔드는 React, API 레이어는 GraphQL을 사용. Django는 백엔드 서비스 프레임워크로서의 역할.

### 종합 판단

Instagram의 Django는 "Django"라는 이름만 같지, 사실상 **Meta가 자체 개발한 고성능 Python 웹 프레임워크**에 가깝다. ORM 교체, Python 런타임 포크(Cinder/CinderX), GC 수정, Immortal Objects 등 Python 생태계의 가장 깊은 레이어까지 손을 대었다. "Django를 쓴다"보다 "Django를 기반으로 한 커스텀 프레임워크를 쓴다"가 더 정확한 표현이다.

### 출처

- [Web Service Efficiency at Instagram with Python - Instagram Engineering](https://instagram-engineering.com/web-service-efficiency-at-instagram-with-python-4976d078e366)
- [Django - Instagram Engineering (tagged posts)](https://instagram-engineering.com/tagged/django)
- [Introducing Immortal Objects for Python - Engineering at Meta](https://engineering.fb.com/2023/08/15/developer-tools/immortal-objects-for-python-instagram-meta/)
- [How the Cinder JIT's function inliner helps us optimize Instagram - Meta Engineering](https://engineering.fb.com/2022/05/02/open-source/cinder-jits-instagram/)
- [CinderX GitHub Repository](https://github.com/facebookincubator/cinderx)
- [Cinder GitHub Repository](https://github.com/facebookincubator/cinder)
- [Django at Instagram - Carl Meyer (DjangoCon 2016)](https://reinout.vanrees.org/weblog/2016/11/04/instagram.html)
- [Instagram scales with Postgres - EDB](https://www.enterprisedb.com/blog/instagram-scales-postgres)
- [How Instagram Scaled Its Infrastructure - ByteByteGo](https://blog.bytebytego.com/p/how-instagram-scaled-its-infrastructure)
- [Is Django useful without the ORM? - Django Forum](https://forum.djangoproject.com/t/is-django-useful-without-the-orm-instagram-case-study/23834)

---

## Q11: MSA → 모놀리스 회귀 트렌드 (2024-2025)

### 조사/보고서 자료

| 출처 | 발행일 | 핵심 수치/결론 | URL |
|------|--------|----------------|-----|
| **O'Reilly 조사** | 2024 | 61% MSA 채택, **29% 모놀리스 회귀** (복잡성이 원인) | [O'Reilly Microservices Adoption](https://www.oreilly.com/radar/microservices-adoption-in-2020/) (2020 보고서가 공개, 2024 수치는 2차 출처에서 인용됨) |
| **CNCF 연간 조사** | 2024 Fall | 클라우드 네이티브 커뮤니티 750명 대상 조사. "42% 조직이 MSA를 더 큰 배포 단위로 통합 중"이라는 수치가 2차 출처에서 인용됨 | [CNCF Annual Survey 2024](https://www.cncf.io/reports/cncf-annual-survey-2024/) |
| **Gartner** | 2025 | 중소 규모 앱 대상 **60% 팀이 MSA 선택을 후회**, 모놀리스가 비용 25% 절감 | [Gartner Peer Community Discussion](https://www.gartner.com/peer-community/post/have-ever-to-walk-back-microservices-re-adopt-more-monolithic-approach-to-architecture-spurred-to-make-decision) |
| **ThoughtWorks Tech Radar** | Vol 31 (2024.10) / Vol 32 (2025.04) | MSA를 "Trial" 단계로 유지 (Adopt으로 승격시키지 않음). "MSA가 기본 선택이 되어서는 안 된다"는 입장 지속 | [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar/techniques/microservices) |
| **InfoQ Architecture Trends** | 2024-2025 | Modular Monolith를 "Early Majority" 트렌드로 분류. Sam Newman: "The monolith is not the enemy" | [InfoQ Architecture Trends 2025](https://www.infoq.com/articles/architecture-trends-2025/) |
| **Statista** | 2024 | 89% 기업이 MSA를 도입했으나 많은 기업이 예상치 못한 도전에 직면 | 2차 출처 인용 |
| **CNCF Service Mesh 지표** | 2023 Q3→2025 Q3 | Service Mesh 채택률 18% → 8%로 하락 (MSA 핵심 인프라 감소 지표) | 2차 출처 인용 |

### 기업 사례

| 기업 | 전환 시기 | 내용 | 결과 |
|------|-----------|------|------|
| **Amazon Prime Video** | 2023 | 비디오 품질 모니터링 서비스를 분산 MSA(AWS Step Functions + S3)에서 모놀리스로 전환 | **비용 90% 절감**. 데이터 전송을 네트워크 대신 인메모리로 처리. 단, Prime Video 전체가 아닌 특정 서비스만 해당. |
| **Segment** | 2018-2020 | 150+ 마이크로서비스를 **단일 서비스(Centrifuge)**로 통합 | 수십억 메시지/일 처리. 온콜 페이징 대폭 감소, 스케일링 단순화. 운영 오버헤드 해소. |
| **Shopify** | 2016-현재 | MSA 대신 **Modular Monolith** 선택. Rails 모놀리스를 컴포넌트 단위로 분리하되 단일 코드베이스 유지 | 30TB/분 처리. 정적 분석으로 모듈 경계 강제. 결제/인증 등 극소수만 별도 서비스로 분리. |
| **Basecamp** | 2023-2024 | 클라우드+MSA에서 모놀리스+자체 서버로 회귀 | 클라우드 비용 대폭 절감 보고 |
| **Google (Service Weaver)** | 2023 | Modular Monolith로 작성하고 MSA로 배포하는 프레임워크 제안 | "양쪽의 장점을 결합"하는 접근법 |

### 종합 평가: [Confirmed] 승격 가능 여부

**"O'Reilly 2024 조사: 61% MSA 채택, 29% 모놀리스 회귀" → [Likely] 유지, [Confirmed] 승격은 보류**

근거:
1. **"61% 채택, 29% 회귀" 수치 자체**는 여러 2차 출처(Medium, foojay.io, byteiota 등)에서 반복 인용되지만, **O'Reilly 공식 보고서 원문 링크를 직접 확인하지 못했다**. O'Reilly 공개 보고서는 2020년 것이 확인되며, 2024년 보고서는 유료이거나 비공개일 가능성이 있다.
2. 그러나 **트렌드 자체는 다수의 독립적 출처에서 교차 확인됨**:
   - CNCF: 42% 통합 중 (2차 출처)
   - Gartner: 60% 후회 (2차 출처)
   - ThoughtWorks: MSA를 Adopt으로 올리지 않는 지속적 입장
   - InfoQ: Modular Monolith를 Early Majority로 분류
   - Amazon, Segment, Shopify 등 실제 사례 다수
3. **정확한 수치(61%, 29%)는 원문 확인 불가이므로 [Confirmed]로 올리기 어렵지만**, "MSA 회귀 트렌드가 실재한다"는 사실 자체는 **[Confirmed]** 수준이다.

**권장사항**: 수치 인용 시 "O'Reilly 2024 조사에 따르면"보다는 "다수의 2024-2025 산업 조사에 따르면, MSA 채택 기업 중 상당수(약 30-40%)가 모놀리스 또는 모듈러 모놀리스로 회귀 중"으로 표현하는 것이 더 정확하다.

### 출처 목록

- [Microservices Consolidation: 42% Return to Monoliths - byteiota](https://byteiota.com/microservices-consolidation-42-return-to-monoliths/)
- [Monolith vs microservices 2025 - Pawel Piwosz (Medium)](https://medium.com/@pawel.piwosz/monolith-vs-microservices-2025-real-cloud-migration-costs-and-hidden-challenges-8b453a3c71ec)
- [Monolith vs Microservices in 2025 - foojay.io](https://foojay.io/today/monolith-vs-microservices-2025/)
- [Amazon Prime Video 90% Cost Reduction - DEV Community](https://dev.to/indika_wimalasuriya/amazon-prime-videos-90-cost-reduction-throuh-moving-to-monolithic-k4a)
- [Return of the Monolith: Amazon Dumps Microservices - The New Stack](https://thenewstack.io/return-of-the-monolith-amazon-dumps-microservices-for-video-monitoring/)
- [Segment: Goodbye Microservices](https://segment.com/blog/goodbye-microservices/)
- [To Microservices and Back Again - Why Segment Went Back - InfoQ](https://www.infoq.com/news/2020/04/microservices-back-again/)
- [Shopify Modular Monolith - InfoQ](https://www.infoq.com/news/2019/07/shopify-modular-monolith/)
- [Under Deconstruction: The State of Shopify's Monolith - Shopify Engineering](https://shopify.engineering/shopify-monolith)
- [ThoughtWorks Technology Radar - Microservices](https://www.thoughtworks.com/radar/techniques/microservices)
- [InfoQ Architecture Trends 2025](https://www.infoq.com/articles/architecture-trends-2025/)
- [InfoQ Architecture Trends 2024](https://www.infoq.com/articles/architecture-trends-2024/)
- [CNCF Annual Survey 2024](https://www.cncf.io/reports/cncf-annual-survey-2024/)
- [Why microservices might be finished - VentureBeat](https://venturebeat.com/data-infrastructure/why-microservices-might-be-finished-as-monoliths-return-with-a-vengeance)
- [From Microservices Hell to Monolith Heaven - XYZBytes](https://www.xyzbytes.com/blog/microservices-to-monolith-migration-2025)
- [Gartner Peer Community - Walking back microservices](https://www.gartner.com/peer-community/post/have-ever-to-walk-back-microservices-re-adopt-more-monolithic-approach-to-architecture-spurred-to-make-decision)

---

# Part 5: Fact Check 결과

Now I have enough data to compile the full fact-check report.

## Fact Check 결과

---

### 정확 ✅

- **clumsysmurf HN 가입일 (2011.7.23) 및 카르마 (8,225)**: WebFetch로 확인. 가입일 July 23, 2011, 카르마 8225 정확 일치.

- **clumsysmurf 스레드 item?id=34298153에서 스코프 관리 관련 반론 제시**: 확인됨. 단일 스코프(singleton)는 수동 DI가 쉽지만, 여러 스코프가 있으면 관리가 tedious하고 error-prone해진다는 주장.

- **Rod Johnson: 호주 출신, 시드니 대학 음악학 PhD (1996)**: Wikipedia 등에서 확인. 시드니 대학에서 BA Hons (음악+CS, 1992), PhD musicology (1996).

- **Rod Johnson 논문 제목 "Piano music in Paris under the July monarchy"**: 정확 확인. 전체 제목은 "Piano music in Paris under the July monarchy (1830-1848)".

- **Rod Johnson 2002년 "Expert One-on-One J2EE Design and Development" 저술**: 정확. 2002년 10월 출간 확인.

- **Spring 오픈소스 공개 시기**: Apache 2.0 라이선스로 **2003년 6월** 첫 릴리스, **2004년 3월** 1.0 출시. 답변의 "2003년 오픈소스 공개, 2004년 1.0 출시"와 일치.

- **SpringSource VMware 인수 2009년**: 확인. 2009년 8월 VMware가 $420M에 인수.

- **Rod Johnson 현재 Embabel CEO**: 확인. Embabel은 JVM용 에이전트 프레임워크.

- **IoC 개념: 1988년 Johnson & Foote 논문 "Designing Reusable Classes"에서 등장**: 정확. Journal of Object-Oriented Programming, 1988년 6/7월호에 게재. "inversion of control"이라는 용어가 이 논문에서 처음 등장한 것으로 Martin Fowler 등이 인용. 단, 저자는 **Ralph Johnson & Brian Foote**이며 Spring의 Rod Johnson과는 **다른 인물**임에 유의.

- **Go의 bouk/monkey가 JMP 명령어를 바이너리에 주입**: 정확. 함수의 첫 번째 명령어를 JMP로 교체하고, mprotect syscall로 메모리 보호를 해제하는 방식.

- **Amazon Prime Video: 비용 90% 절감**: 정확. 2023년 VQA(Video Quality Analysis) 모니터링 서비스를 마이크로서비스에서 모놀리스로 전환하여 인프라 비용 90%+ 절감.

- **Segment: 150+ MSA에서 단일 서비스로 회귀**: 정확. InfoQ, Segment 공식 블로그 등에서 확인. 운영 오버헤드가 너무 커서 모놀리스로 복귀.

- **Shopify: Modular Monolith**: 정확. Ruby on Rails 기반 280만 줄 코드베이스를 모듈형 모놀리스로 구조화. Packwerk으로 경계 관리.

- **Instagram: 현재도 Django 사용 (극도로 커스텀)**: 확인. CinderX가 Instagram Django 서비스에서 프로덕션 사용 중.

- **Instagram: CPython 포크 (Cinder/CinderX)**: 정확. Cinder는 Meta의 CPython 포크였고, 현재는 CinderX라는 Python 확장으로 진화. Python 3.14부터 stock CPython 지원.

- **Instagram: Immortal Objects**: 정확. PEP 683으로 Python에 기여. 포크 서버 워크로드에서 참조 카운트 업데이트에 의한 copy-on-write를 줄여 메모리 사용량 감소.

- **Spring Boot 기본 앱 ~107개 빈**: Spring 공식 블로그에서 확인. 수동 설정 시 51개, 전체 자동 설정 시 107개 (actuator 제외).

- **Java ByteBuddy, Java Agent를 통한 바이트코드 조작**: 정확. ByteBuddy는 대표적인 바이트코드 조작 라이브러리.

---

### 부정확/수정 필요 ❌

- **"JDK 17+ 이후 동적 agent attach 제한"**: **부정확**. 동적 에이전트 로딩 제한은 **JDK 21**(JEP 451)부터 경고가 발생하며, 향후 릴리스에서 기본 비활성화 예정. JDK 17에서는 아무런 제한이나 경고 없이 동적 에이전트 로딩이 가능함. 정확한 표현은 "JDK 21+ 이후 동적 agent attach 제한(경고)" — 출처: [JEP 451](https://openjdk.org/jeps/451)

---

### 미확인 ⚠️

- **Gartner 2025: "60% 후회 (중소 규모 앱)"**: 검증 불가. Gartner에서 "60% 기술 구매 후회" 조사(2023)는 존재하나, 이는 서비스 구독 갱신에 대한 것이지 마이크로서비스 도입 후회와는 무관. 마이크로서비스에 특화된 60% 후회 통계는 공개 자료에서 확인 불가. Gartner 유료 보고서에 있을 가능성은 있으나, 공개 출처로는 검증 불가.

- **spring-boot-autoconfigure에 122개 자동 구성 클래스**: 구체적인 숫자 122개는 공개 검색으로 확인 불가. Spring Boot 버전에 따라 자동 구성 클래스 수가 다르므로 특정 버전에서는 맞을 수 있으나 검증 불가.

- **Web + JPA + Security + Actuator = 200~400개 빈**: 구체적인 범위를 검증하는 공개 출처를 찾지 못함. 의존성 추가 시 빈 수가 증가하는 것은 사실이나, 200~400이라는 범위의 정확성은 미확인.

- **Instagram 커스텀 ORM**: Instagram이 Django ORM을 극도로 커스텀했다는 것은 널리 알려져 있으나, 완전한 "커스텀 ORM"인지 "커스텀된 Django ORM"인지는 공개 자료로 정확히 확인 불가.

- **EJB 2.0에서 3개 파일 필수 (Home, Remote, Bean) + XML / JNDI 룩업 5단계**: EJB 2.0에서 Home Interface, Remote Interface, Bean Class가 필수였고 XML 배포 기술자가 필요했던 것은 사실이나, "JNDI 룩업 5단계"의 정확한 단계 수는 구현에 따라 다를 수 있어 정확한 수치는 미확인.

---

### 요약

| 카테고리 | 건수 |
|---------|------|
| 정확 ✅ | 17건 |
| 부정확 ❌ | 1건 (JDK 17 → JDK 21이 정확) |
| 미확인 ⚠️ | 5건 |

가장 주요한 오류는 **동적 에이전트 로딩 제한이 JDK 17+가 아니라 JDK 21+(JEP 451)부터**라는 점입니다.

---

> **참고**: Q5(정적 타입 monkey patching)와 Q9(uber-go/fx)의 상세 내용은 `develop/go/monkey-patching-and-uber-fx-deep-dive.md`에 별도 작성되어 있습니다.
