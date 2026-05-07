#ifndef LRU_VARIANTS_H
#define LRU_VARIANTS_H

#include <unordered_map>
#include <unordered_set>
#include <list>
#include <random>
#include "cache.h"
#include "adaptsize_const.h" /* AdaptSize constants */



typedef std::list<uint64_t >::iterator ListIteratorType;
typedef std::unordered_map<uint64_t , ListIteratorType> lruCacheMapType;


using namespace std;
/*
  LRU: Least Recently Used eviction
*/
class LRUCache : public Cache
{
protected:
    // list for recency order
    std::list<uint64_t > _cacheList;
    // map to find objects in list
    lruCacheMapType _cacheMap;
    unordered_map<uint64_t , uint64_t > _size_map;


    virtual void hit(lruCacheMapType::const_iterator it, uint64_t size);

public:
    LRUCache()
        : Cache()
    {
    }
    virtual ~LRUCache()
    {
    }

    bool lookup(const SimpleRequest &req) override;

    bool exist(const int64_t &key) override;

    void admit(const SimpleRequest &req) override;

    void evict(const int64_t &obj);

    void evict();

    SimpleRequest evict_return();
};

// static Factory<LRUCache> factoryLRU("LRU");



/*
  AdaptSize: ExpLRU with automatic adaption of the _cParam
*/
class AdaptSizeCache : public LRUCache
{
public:
    AdaptSizeCache();
    virtual ~AdaptSizeCache()
    {
    }

    virtual void setPar(std::string parName, std::string parValue);
    virtual bool lookup(const SimpleRequest &);
    virtual void admit(const SimpleRequest &);

private:
    double _cParam; //
    uint64_t statSize;
    uint64_t _maxIterations;
    uint64_t _reconfiguration_interval;
    uint64_t _nextReconfiguration;
    double _gss_v;  // golden section search book parameters
    // for random number generation
    std::uniform_real_distribution<double> _uniform_real_distribution =
            std::uniform_real_distribution<double>(0.0, 1.0);

    struct ObjInfo {
        double requestCount; // requestRate in adaptsize_stub.h
        uint64_t objSize;

        ObjInfo() : requestCount(0.0), objSize(0) { }
    };
    std::unordered_map<uint64_t , ObjInfo> _longTermMetadata;
    std::unordered_map<uint64_t , ObjInfo> _intervalMetadata;

    void reconfigure();
    double modelHitRate(double c);

    // align data for vectorization
    std::vector<double> _alignedReqCount;
    std::vector<double> _alignedObjSize;
    std::vector<double> _alignedAdmProb;
};

// static Factory<AdaptSizeCache> factoryAdaptSize("AdaptSize");

#endif
