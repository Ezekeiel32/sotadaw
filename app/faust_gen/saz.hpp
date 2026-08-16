/* ------------------------------------------------------------
name: "saz"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Saz -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Saz_H__
#define  __Saz_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Saz
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Saz_faustpower2_f(float value) {
	return value * value;
}

class Saz : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fHslider0;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec3[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec4[2];
	int IOTA0;
	float fVec1[512];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst11;
	float fRec2[3];
	float fRec5[2];
	float fVec2[4096];
	float fRec1[3];
	float fRec7[3];
	float fRec8[2];
	float fVec3[4096];
	float fRec6[3];
	float fRec0[3];
	float fConst12;
	float fConst14;
	float fConst16;
	float fConst18;
	float fRec9[3];
	float fConst19;
	FAUSTFLOAT fHslider3;
	
 public:
	Saz() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Saz -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "saz.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "saz");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(1350.8849f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Saz_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -0.2f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 0.2f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 21991.148f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.0028f * fConst0);
		fConst11 = 0.16f * fConst0;
		fConst12 = 0.3f / (fConst1 * fConst5);
		float fConst13 = std::tan(565.4867f / fConst0);
		fConst14 = 2.0f * (1.0f - 1.0f / Saz_faustpower2_f(fConst13));
		float fConst15 = 1.0f / fConst13;
		fConst16 = (fConst15 + -0.25f) / fConst13 + 1.0f;
		float fConst17 = (fConst15 + 0.25f) / fConst13 + 1.0f;
		fConst18 = 1.0f / fConst17;
		fConst19 = 0.4f / (fConst13 * fConst17);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.8f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.3f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec3[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec4[l2] = 0;
		}
		IOTA0 = 0;
		for (int l3 = 0; l3 < 512; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 4096; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec1[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 4096; l10 = l10 + 1) {
			fVec3[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec6[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec9[l13] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Saz* clone() {
		return new Saz();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("saz");
		ui_interface->addHorizontalSlider("bowl", &fHslider3, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(7e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider0, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("shimmer", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst7 * (0.35f * fSlow0 + 0.65f));
		float fSlow2 = 2.0f * (1.0f - 1.0f / Saz_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.4142135f) / fSlow1 + 1.0f);
		float fSlow6 = float(fButton0);
		float fSlow7 = float(fHslider2);
		float fSlow8 = std::max<float>(7e+01f, fSlow7 * (0.0022f * float(fHslider1) + 1.0018f));
		int iSlow9 = int(std::max<float>(1.0f, fConst11 / fSlow8));
		float fSlow10 = 1.0f - fSlow3;
		float fSlow11 = 1.0f / (fSlow3 + 1.0f);
		float fSlow12 = std::max<float>(2.0f, fConst0 / fSlow8 + -2.0f);
		float fSlow13 = fSlow12 + -1.499995f;
		int iSlow14 = int(fSlow13);
		int iSlow15 = std::min<int>(4096, std::max<int>(0, iSlow14 + 4));
		float fSlow16 = std::floor(fSlow13);
		float fSlow17 = fSlow12 + (-3.0f - fSlow16);
		float fSlow18 = fSlow12 + (-2.0f - fSlow16);
		float fSlow19 = fSlow12 + (-1.0f - fSlow16);
		float fSlow20 = fSlow12 - fSlow16;
		float fSlow21 = fSlow20 * fSlow19;
		float fSlow22 = fSlow21 * fSlow18;
		float fSlow23 = 0.041666668f * fSlow22 * fSlow17;
		int iSlow24 = std::min<int>(4096, std::max<int>(0, iSlow14 + 3));
		float fSlow25 = 0.16666667f * fSlow22;
		int iSlow26 = std::min<int>(4096, std::max<int>(0, iSlow14 + 2));
		float fSlow27 = 0.25f * fSlow21;
		int iSlow28 = std::min<int>(4096, std::max<int>(0, iSlow14 + 1));
		float fSlow29 = 0.16666667f * fSlow20;
		int iSlow30 = std::min<int>(4096, std::max<int>(0, iSlow14));
		float fSlow31 = 0.041666668f * fSlow19;
		float fSlow32 = fSlow12 + (-4.0f - fSlow16);
		float fSlow33 = std::max<float>(7e+01f, fSlow7);
		int iSlow34 = int(std::max<float>(1.0f, fConst11 / fSlow33));
		float fSlow35 = std::max<float>(2.0f, fConst0 / fSlow33 + -2.0f);
		float fSlow36 = fSlow35 + -1.499995f;
		int iSlow37 = int(fSlow36);
		int iSlow38 = std::min<int>(4096, std::max<int>(0, iSlow37 + 4));
		float fSlow39 = std::floor(fSlow36);
		float fSlow40 = fSlow35 + (-3.0f - fSlow39);
		float fSlow41 = fSlow35 + (-2.0f - fSlow39);
		float fSlow42 = fSlow35 + (-1.0f - fSlow39);
		float fSlow43 = fSlow35 - fSlow39;
		float fSlow44 = fSlow43 * fSlow42;
		float fSlow45 = fSlow44 * fSlow41;
		float fSlow46 = 0.041666668f * fSlow45 * fSlow40;
		int iSlow47 = std::min<int>(4096, std::max<int>(0, iSlow37 + 3));
		float fSlow48 = 0.16666667f * fSlow45;
		int iSlow49 = std::min<int>(4096, std::max<int>(0, iSlow37 + 2));
		float fSlow50 = 0.25f * fSlow44;
		int iSlow51 = std::min<int>(4096, std::max<int>(0, iSlow37 + 1));
		float fSlow52 = 0.16666667f * fSlow43;
		int iSlow53 = std::min<int>(4096, std::max<int>(0, iSlow37));
		float fSlow54 = 0.041666668f * fSlow42;
		float fSlow55 = fSlow35 + (-4.0f - fSlow39);
		float fSlow56 = float(fHslider3);
		float fSlow57 = 1.0f - 0.5f * fSlow56;
		float fSlow58 = 0.62f * fSlow0;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow6;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow6 <= fVec0[1]) + (fSlow6 > fVec0[1]);
			float fTemp0 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp1 = float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f));
			fVec1[IOTA0 & 511] = fTemp1;
			fRec2[0] = 2.3283064e-10f * (fTemp1 - fVec1[(IOTA0 - iSlow9) & 511]) - fSlow5 * (fSlow4 * fRec2[2] + fSlow2 * fRec2[1]);
			fRec5[0] = -(fSlow11 * (fSlow10 * fRec5[1] - (fRec1[1] + fRec1[2])));
			float fTemp2 = 0.9955f * fRec5[0] + fSlow5 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]);
			fVec2[IOTA0 & 4095] = fTemp2;
			fRec1[0] = fSlow32 * (fSlow17 * (fSlow18 * (fSlow31 * fVec2[(IOTA0 - iSlow30) & 4095] - fSlow29 * fVec2[(IOTA0 - iSlow28) & 4095]) + fSlow27 * fVec2[(IOTA0 - iSlow26) & 4095]) - fSlow25 * fVec2[(IOTA0 - iSlow24) & 4095]) + fSlow23 * fVec2[(IOTA0 - iSlow15) & 4095];
			fRec7[0] = 2.3283064e-10f * (fTemp1 - fVec1[(IOTA0 - iSlow34) & 511]) - fSlow5 * (fSlow4 * fRec7[2] + fSlow2 * fRec7[1]);
			fRec8[0] = -(fSlow11 * (fSlow10 * fRec8[1] - (fRec6[1] + fRec6[2])));
			float fTemp3 = 0.9955f * fRec8[0] + fSlow5 * (fRec7[2] + fRec7[0] + 2.0f * fRec7[1]);
			fVec3[IOTA0 & 4095] = fTemp3;
			fRec6[0] = fSlow55 * (fSlow40 * (fSlow41 * (fSlow54 * fVec3[(IOTA0 - iSlow53) & 4095] - fSlow52 * fVec3[(IOTA0 - iSlow51) & 4095]) + fSlow50 * fVec3[(IOTA0 - iSlow49) & 4095]) - fSlow48 * fVec3[(IOTA0 - iSlow47) & 4095]) + fSlow46 * fVec3[(IOTA0 - iSlow38) & 4095];
			float fTemp4 = fRec6[0] + 0.85f * fRec1[0];
			fRec0[0] = fTemp4 - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			fRec9[0] = fTemp4 - fConst18 * (fConst16 * fRec9[2] + fConst14 * fRec9[1]);
			float fTemp5 = fSlow58 * (fSlow57 * fTemp4 + fSlow56 * (fConst19 * (fRec9[0] - fRec9[2]) + fConst12 * (fRec0[0] - fRec0[2])));
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			fVec0[1] = fVec0[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			IOTA0 = IOTA0 + 1;
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
		}
	}

};

#endif
